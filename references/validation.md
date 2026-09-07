# Current verification

## Reproduce

From the skill directory, use Python 3.11+ with `requirements.txt`:

```powershell
python -X utf8 -m unittest discover -s scripts -p "test_*.py"
python -X utf8 scripts/capabilities.py --check
python -X utf8 scripts/replay_acceptance.py --output '<new-private-directory>'
```

The full suite exercises bounded mechanics, ingestion, character/background packs, authoring manifests, ledger transactions, evidence dependencies and read-only session review. Two twenty-turn campaign replays use explicitly simulated dice and check cold-process recovery. They do not certify every system interaction or play quality. Live-player evaluation remains outside the requested acceptance scope.

## Current extension

The evidence tests cover alternative and joint requirements, unsupported cycles and external seeds, single-evidence bottlenecks, unavailable evidence, invalid references, split knowledge and public field projection. Session-review tests cover public/private isolation, Chinese database paths, rollback and branch restoration, provenance, revision filtering and read-only operation.

Executed on 2026-09-07: all 118 tests passed. Both twenty-turn CoC and D&D replays passed with fresh-process recovery at turn ten (final HP 8 and 12 respectively). Skill-creator `quick_validate.py` passed using the installed system Python; the bundled artifact runtime lacked PyYAML, so it was not used for that validator. The test suite and replays used the bundled runtime with the required document libraries. No live players or new original-rulebook source audits are claimed.

Earlier source checks and development counts are retained in [validation history](validation-history.md), not presented as newly executed checks. Current feature scope is generated in [coverage](coverage.md).
