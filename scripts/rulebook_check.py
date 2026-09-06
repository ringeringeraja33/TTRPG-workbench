"""Validate an explicit rulebook manifest. No prose inference or expression evaluation."""
import argparse
import json
from pathlib import Path

FIELDS = ('trigger', 'authority', 'inputs', 'procedure', 'costs', 'outcomes',
          'duration', 'exceptions', 'example', 'boundary')


def audit(project, base, changed=None):
    errors = []
    def require(ok, message):
        if not ok:
            errors.append(message)
        return bool(ok)
    def integer(v):
        return type(v) is int and v > 0
    def file_path(value):
        if not isinstance(value, str) or not value:
            errors.append('missing file path')
            return None
        try:
            path = (base / value).resolve()
            path.relative_to(base.resolve())
            if not path.is_file() or not path.read_text(encoding='utf-8').strip():
                raise ValueError('missing or empty file')
            return path
        except (OSError, ValueError, UnicodeError):
            errors.append('unsafe, missing, empty or non-UTF8 file: ' + value)
            return None
    if not isinstance(project, dict):
        return {'status': 'invalid', 'errors': ['project must be an object'], 'affected': []}
    require(integer(project.get('version')), 'version must be positive integer')
    def records(key, nonempty=True):
        data = project.get(key)
        if not require(isinstance(data, list) and (bool(data) or not nonempty), key + ' must be a list'):
            return {}
        result = {}
        for rec in data:
            if not isinstance(rec, dict) or not isinstance(rec.get('id'), str) or not rec['id'].strip():
                errors.append('invalid record in ' + key)
                continue
            if rec['id'] in result:
                errors.append('duplicate ' + key + ' id: ' + rec['id'])
            result[rec['id']] = rec
        return result
    rules = records('rules')
    artifacts = records('artifacts')
    issues = records('issues', False)
    paths, graph = {}, {}
    for rid, rule in rules.items():
        paths[rid] = file_path(rule.get('file'))
        require(integer(rule.get('revision')), 'invalid rule revision: ' + rid)
        contract = rule.get('contract', {})
        for field in FIELDS:
            require(isinstance(contract, dict) and isinstance(contract.get(field), str)
                    and bool(contract[field].strip()), rid + ' missing contract ' + field)
        deps = rule.get('depends_on')
        if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps):
            errors.append('invalid dependencies: ' + rid)
            deps = []
        graph[rid] = deps
        for dep in deps:
            require(dep in rules, rid + ' unknown dependency: ' + dep)
    visiting, done = set(), set()
    def visit(rid):
        if rid in visiting:
            errors.append('dependency cycle: ' + rid)
            return
        if rid in done or rid not in graph:
            return
        visiting.add(rid)
        for dep in graph[rid]:
            visit(dep)
        visiting.remove(rid)
        done.add(rid)
    for rid in rules:
        visit(rid)
    def closure(ids):
        found = set(ids)
        todo = list(ids)
        while todo:
            for dep in graph.get(todo.pop(), []):
                if dep not in found:
                    found.add(dep)
                    todo.append(dep)
        return found
    claims, bound, artifact_paths = {}, set(), {}
    for aid, artifact in artifacts.items():
        artifact_paths[aid] = file_path(artifact.get('file'))
        require(artifact.get('audience') in ('player', 'gm'), 'invalid audience: ' + aid)
        bindings = artifact.get('bindings')
        if not isinstance(bindings, dict):
            errors.append('invalid bindings: ' + aid)
            bindings = {}
        for rid, rev in bindings.items():
            bound.add(rid)
            require(rid in rules, aid + ' unknown binding: ' + rid)
            if rid in rules:
                require(integer(rev) and rev == rules[rid].get('revision'), aid + ' stale binding: ' + rid)
        values = artifact.get('claims', {})
        if not isinstance(values, dict):
            errors.append('invalid claims: ' + aid)
            values = {}
        for key, value in values.items():
            canonical = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)
            if key in claims and claims[key][0] != canonical:
                errors.append('conflicting claim: ' + key + ' in ' + claims[key][1] + ' / ' + aid)
            claims[key] = (canonical, aid)
    gm_paths = {artifact_paths[k] for k, a in artifacts.items() if a.get('audience') == 'gm'} - {None}
    for aid, artifact in artifacts.items():
        if artifact.get('audience') == 'player':
            require(artifact_paths[aid] not in gm_paths, 'shared player/GM file: ' + aid)
            bindings = artifact.get('bindings', {})
            for rid in closure(bindings if isinstance(bindings, dict) else []):
                require(paths.get(rid) not in gm_paths, aid + ' depends on GM rule: ' + rid)
    for rid in rules:
        require(rid in bound, 'unbound rule: ' + rid)
    for iid, issue in issues.items():
        require(type(issue.get('material')) is bool, 'invalid material flag: ' + iid)
        require(issue.get('status') in ('open', 'resolved'), 'invalid issue status: ' + iid)
        require(isinstance(issue.get('evidence'), str) and bool(issue['evidence'].strip()), 'missing evidence: ' + iid)
        require(not (issue.get('material') is True and issue.get('status') == 'open'), 'open material issue: ' + iid)
    affected = []
    if changed is not None:
        require(changed in rules, 'unknown changed ID: ' + changed)
        impacted = {rid for rid in rules if changed in closure([rid])}
        affected = sorted(aid for aid, a in artifacts.items()
                          if isinstance(a.get('bindings'), dict) and impacted.intersection(a['bindings']))
    return {'status': 'invalid' if errors else 'passed explicit checks', 'errors': errors, 'affected': affected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--changed')
    args = parser.parse_args()
    try:
        project = json.loads(args.manifest.read_text(encoding='utf-8'),
                             parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        result = audit(project, args.manifest.parent, args.changed)
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        result = {'status': 'invalid', 'errors': [str(exc)], 'affected': []}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(result['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
