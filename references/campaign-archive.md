# Campaign backups and integrity checks

Use `scripts/campaign_archive.py` for a consistent SQLite backup and read-only ledger checks. The archive contains the entire GM campaign history, including private observations and pending actions; store it as a private file.

```powershell
python -X utf8 scripts/campaign_archive.py campaign.sqlite check
python -X utf8 scripts/campaign_archive.py campaign.sqlite backup --output private-backups/session-12.sqlite
python -X utf8 scripts/campaign_archive.py private-backups/session-12.sqlite check --expected-sha256 <file_sha256-from-backup>
```

Backup uses SQLite's backup API, so committed data in WAL is included. It exclusively creates a new destination, validates the copied ledger, and returns revision, snapshot hash and file SHA-256 without printing GM content. Existing destinations and the source itself are rejected. If validation fails, only the newly created copy is removed; the source is retained. A backup reflects a consistent committed database state and may exclude operations committed after that snapshot.

To recover, first check the archived file against the hash saved separately when it was created. Then use the same backup command to copy that archive to a **new working database filename**, and point the ordinary session/action tools at that file. Pending choices, dice evidence, source receipts and revision history remain intact. Recovery does not reroll dice or reapply resource costs. The original working campaign remains available until the operator chooses which branch to continue.

Checks cover SQLite integrity, contiguous revisions from zero, initial receipt hash, per-event identity/revision/request hash, unchanged rules profile, snapshot schema validity and restore snapshots matching their referenced target. Every historical state is checked, so runtime grows with history size. Diagnostics identify the failing revision without echoing event contents.

These checks do not replay every state transition, authenticate authors or prove that a valid-looking snapshot follows from its event. The existing ledger does not cryptographically bind every historical snapshot to an external trusted record. A file hash saved separately detects byte changes to an archive; an attacker who changes both the file and the recorded hash defeats that comparison. Expected file hashes are intended for closed archive files, not actively changing databases or separate WAL files. The snapshot hash is a useful comparison identifier, not proof of fair dice or correct rule adjudication.

No automatic scheduling, retention/deletion policy, encryption or cloud upload is included. Run backup explicitly at meaningful session checkpoints. Thirteen tests cover read-only checks, pending-action recovery, WAL, overwrite prevention, corruption, restore consistency, failed-copy cleanup, independent hashes and fresh-process CLI recovery.

This command accepts campaign ledgers with the `events` table. Independent Dice/card databases have different schemas and must be backed up separately; a campaign archive is not a complete workspace backup.

The current local Dice dialect now has its own [archive command](dice-archive.md); it shares the exclusive SQLite copy mechanism but uses a distinct validator.
