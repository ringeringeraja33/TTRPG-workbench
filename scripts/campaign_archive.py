"""Read-only ledger checks and exclusive consistent SQLite backups.

Checks detect structural corruption; they do not authenticate GM decisions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import session


def connect_readonly(path):
    path=Path(path).resolve()
    if not path.is_file():raise ValueError('Campaign database missing')
    return sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,timeout=10)


def file_digest(path):
    result=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):result.update(block)
    return result.hexdigest()


def check(path,expected_sha256=None):
    if expected_sha256 is not None:
        if not isinstance(expected_sha256,str) or len(expected_sha256)!=64 or any(c not in '0123456789abcdefABCDEF' for c in expected_sha256):
            raise ValueError('Expected SHA-256 must contain 64 hexadecimal characters')
        if file_digest(path)!=expected_sha256.lower():raise ValueError('Archive file checksum mismatch')
    db=connect_readonly(path)
    try:
        db.execute('BEGIN')
        if db.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:raise ValueError('SQLite integrity check failed')
        rows=db.execute('SELECT revision,id,request_hash,request,state FROM events ORDER BY revision')
        expected=0;profile=None;last=None
        for revision,eid,request_hash,raw_request,raw_state in rows:
            if type(revision) is not int or revision!=expected:raise ValueError('Ledger revisions must be contiguous from zero')
            try:
                state=json.loads(raw_state);request=json.loads(raw_request)
                session.validate(state)
                if revision==0:
                    if eid!='__init__' or request!={'kind':'init'} or request_hash!=session.digest(state):
                        raise ValueError('Invalid initialization receipt')
                    profile=state['profile']
                else:
                    required={'id','revision','profile','input','resolution','sources','changes'}
                    if not isinstance(request,dict) or set(request)!=required or not isinstance(eid,str) or not eid or eid.startswith('__'):
                        raise ValueError('Invalid event contract')
                    if request['id']!=eid or type(request['revision']) is not int or request['revision']!=revision-1:
                        raise ValueError('Event identity or revision mismatch')
                    if request_hash!=session.digest(request):raise ValueError('Event request checksum mismatch')
                    if request['profile']!=profile or state['profile']!=profile:raise ValueError('Rules profile changed')
                    if any(not isinstance(request[k],str) or not request[k] for k in ('input','resolution')):
                        raise ValueError('Missing event adjudication')
                    if not isinstance(request['sources'],list) or not request['sources'] or any(not isinstance(s,str) or not s.strip() for s in request['sources']):
                        raise ValueError('Missing event sources')
                    if not isinstance(request['changes'],list) or any(not isinstance(c,dict) for c in request['changes']):raise ValueError('Invalid event changes')
                    restores=[c for c in request['changes'] if c.get('kind')=='restore']
                    if restores:
                        if len(request['changes'])!=1 or set(restores[0])!={'kind','revision'}:raise ValueError('Invalid restore receipt')
                        target=restores[0]['revision'];session.integer(target)
                        if target>=revision:raise ValueError('Restore references a future revision')
                        old=db.execute('SELECT state FROM events WHERE revision=?',(target,)).fetchone()
                        if old is None or json.loads(old[0])!=state:raise ValueError('Restored snapshot differs from target')
            except (ValueError,KeyError,TypeError) as exc:
                # Do not echo private event contents or rule text in diagnostics.
                raise ValueError(f'Invalid ledger record at revision {revision}') from exc
            expected+=1;last=state
        if last is None:raise ValueError('Empty campaign ledger')
        return {'ok':True,'revision':expected-1,'records':expected,'state_sha256':session.digest(last),
                'scope':'SQLite integrity, snapshot schemas, event hashes, revision/profile continuity and restore equality; not event replay or authenticity'}
    finally:db.close()


def backup(source,output,validator=check):
    output=Path(output)
    if Path(source).resolve()==output.resolve():raise ValueError('Backup must use a different destination')
    original=connect_readonly(source)
    created=False
    try:
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('xb'):pass
        created=True
        destination=sqlite3.connect(output)
        try:original.backup(destination)
        finally:destination.close()
        result=validator(output)
        result.update(backup_saved=True,file_sha256=file_digest(output))
        return result
    except Exception:
        if created:output.unlink(missing_ok=True)
        raise
    finally:original.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('database',type=Path)
    sub=parser.add_subparsers(dest='command',required=True)
    c=sub.add_parser('check');c.add_argument('--expected-sha256')
    b=sub.add_parser('backup');b.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=check(args.database,args.expected_sha256) if args.command=='check' else backup(args.database,args.output)
    print(session.encode(result))


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    try:main()
    except (ValueError,KeyError,TypeError,OSError,sqlite3.Error) as exc:
        print(session.encode({'error':str(exc)}),file=sys.stderr);raise SystemExit(2)
