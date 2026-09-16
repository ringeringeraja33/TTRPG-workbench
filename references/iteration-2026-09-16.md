# Autonomous iteration record — 2026-09-16

The user authorized the agent to choose inspection, extension and repeat-validation rounds. This batch used three bounded passes. Existing local changes were preserved; no commit or push was performed.

1. Inspection and repair: exploration snapshots previously checked containers but omitted historical expense structure, acknowledgement contents and temporal consistency. Validation now rejects malformed receipts and impossible intervals/statuses. Historical expenses do not require current affordability; otherwise a valid old expense could invalidate a depleted character.
2. Extension: exploration preview applies the exact event to a consistent temporary SQLite backup and reports minutes, resource changes and reminders to a private file. Commit remains an explicit ledger apply with existing revision/idempotency checks. Pending reminder rescheduling preserves identity and acknowledgements and records an explicit reason in the ledger. Due reminders cannot be rescheduled to bypass their consequence.
3. Integration validation: an original eight-transition scenario checks preview isolation, duplicate submission, fresh-process recovery, deadline blocking, rescheduling, an action expense with time advancement, exhausted supplies and player secrecy. Existing campaign walkthroughs were rerun successfully.

Verification: 285 unit/integration tests, exploration/action/combat replays, two twenty-turn campaign replays, eight Keeper cases, capability freshness and diff whitespace checks passed. These are scripted checks; they do not establish full rules coverage or live-player experience.

## Next priorities

These remain candidate work, not completed capabilities:

- Live investigation expansion completed in the following batch: new evidence/conclusions/routes, unseen-only editing, 14 new tests and a seven-transition recovery replay. Existing receipts and hypotheses remain unchanged.
- Improve character-derived-stat dependencies and advancement previews with explicit edition profiles and authoritative rule sources.
- Add long-term projects and downtime only after defining interruption, resource reservation and shared-time behavior.
- Build a local interaction surface after stabilizing the event contracts, including player-safe projection checks.

For each next batch: inspect the affected contracts, implement a bounded improvement, exercise failure/recovery paths, then run relevant regressions. Stop the batch at a verified coherent result; escalate only a material decision requiring user input. Do not treat passing tests as evidence that all TTRPG rules are implemented.

## Partial character update batch

Added a bounded partial-update preview using a single ledger snapshot. Full stat records merge by ID, explicit removals remain guarded, existing resource updates accept only maxima, and unspecified fields are retained. A deterministic concurrent-update test verifies stale plans fail without overwriting new damage. Thirteen new tests brought the suite to 312; all six replay scripts and capability/diff checks passed. Derived-stat rules and advancement legality remain future work.

## Campaign archive batch

Implemented read-only historical checks and exclusive SQLite backup without rerolling actions. Tests cover WAL and recovery to a separate file. All 325 tests passed; six existing campaign replay databases passed historical checks and an archive roundtrip preserved the full exploration state. Separate Dice storage, encrypted backups and automatic retention remain outside scope.

## Local Dice archive batch

Reused the exclusive SQLite archive writer with a separate current-Dice validator. Cards, logs, scopes and operation receipts survive copying; original operation retries and receipt imports do not reroll. All 338 tests passed, and an existing action-replay Dice archive passed checksum verification. Paired cross-database snapshots, path rebinding and the legacy accounts dialect remain outside scope.

## Unified acceptance batch

Three passes: introduced a repeatable eight-stage runner; added five negative-path tests for the runner; reran the entire workflow in a new output directory. Final results: 343 tests, all six replay scripts and 15 archive roundtrips passed. Future development batches can reuse this entry point after bounded fixes instead of requiring the user to approve each verification stage. No background scheduler was created.
