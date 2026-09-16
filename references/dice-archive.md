# Current local Dice archives

`scripts/dice_archive.py` backs up the current `dice_local.py` SQLite dialect, including local tables, character cards, logs, pending table tools and committed operation receipts. It does not convert or accept the older `dicebot.py` accounts schema.

```powershell
python -X utf8 scripts/dice_archive.py dice.sqlite check
python -X utf8 scripts/dice_archive.py dice.sqlite backup --output private-backups/dice-session-12.sqlite
python -X utf8 scripts/dice_archive.py private-backups/dice-session-12.sqlite check --expected-sha256 <saved-file-hash>
```

The shared archive writer uses SQLite backup, includes committed WAL data, never overwrites an existing destination, validates the copy and removes only its newly created copy if validation fails. The report contains aggregate counts and a file checksum, not cards, actor IDs or hidden rolls. The database itself is private and contains all scopes.

Checks cover database integrity, current schema dialect, basic state containers, active card/log references, request/response shapes, operation identities and contiguous per-table revisions. They do not fully validate every nested card/tool field, replay commands, prove the correctness of stored dice or authenticate history. Save the file hash separately and use it against closed archive files; it is not a trusted signature.

Restore by copying a verified archive to a new working database using the same backup command. Existing operation IDs and responses survive, so retrying the identical original command returns the stored response without rolling again. Scope names, actor identities, cards and logs are preserved. Use the exact original command, expected revision and operation ID when retrying an existing operation.

## Pairing with a campaign ledger

Back up both the [campaign ledger](campaign-archive.md) and local Dice database during a quiet checkpoint when no commands are being submitted. These two files are copied independently, not in a cross-database atomic transaction. Record which two copies belong together; do not assume a pair taken while play continues has matching latest receipts.

Already imported action evidence is stored inside the campaign ledger and does not need to be rolled again. An action declaration that has not yet imported its receipt still contains the original absolute Dice database path. Copying a database to a new filename does **not** rewrite that declaration. A new action can explicitly refer to the recovered file; for an existing unrolled declaration, cancel it through the normal action workflow and redeclare against the recovered path, preserving its adjudication and intended receipt. Do not directly rewrite ledger history. A receipt already consumed in the active campaign branch remains protected against duplicate use even if its database is copied.

No automatic path rebinding, combined campaign/Dice snapshot, legacy-card migration, encryption or retention scheduler is provided. Thirteen tests cover card/log recovery, raw receipt bridge compatibility, no-reroll retry, multiple scopes, WAL, privacy, damaged receipts, destination protection, invalid-copy cleanup, schema isolation and independent file hashes.
