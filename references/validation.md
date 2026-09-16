# Current verification

## Unified acceptance runner (2026-09-16)

The new verification runner completed two full runs. The final run passed all 343 tests, capability freshness and all six replay scripts, followed by 15 generated-database archive/hash/state roundtrips. Five new runner tests verify failure continuation, timeout reporting, rejection of existing/repository outputs and refusal to pass without database artifacts. See [repeatable acceptance](verification-runner.md). Outputs were retained in separate private directories outside the repository.

## Current Dice archive support (2026-09-16)

All 338 tests passed, including 13 new Dice archive tests for card/log preservation, no-reroll retries, receipt import from a recovered path, per-table consistency, WAL, corruption, privacy and dialect isolation. An existing action-replay Dice database also passed backup and independent file-hash verification. Capability generation/check and diff whitespace checks passed. See [Dice archive limitations](dice-archive.md), including separate campaign checkpoints and unrebound absolute receipt paths.

## Campaign archives and historical integrity (2026-09-16)

All 325 tests passed, including 13 new archive tests covering read-only checks, WAL backup, pending dice evidence, corruption, overwrite protection, cleanup, checksums and cold recovery. The checker also passed against six existing campaign databases from action, combat, exploration, investigation and both twenty-turn replays. An exploration database backup matched the original full state and passed its independent file-hash check. Capability generation/check and diff whitespace checks passed. Separate Dice databases are outside this archive contract. See [archive scope](campaign-archive.md); checks do not authenticate history or replay all transitions.

## Partial character advancement previews (2026-09-16)

All 312 tests passed, including 13 new partial-update tests. Checks cover preservation of unspecified fields, explicit stat deletion, resource capacity changes, one-snapshot merging under a concurrent ledger update, private CLI preview, cold apply and restore. Action/combat/exploration/investigation replays, both twenty-turn campaign replays and eight Keeper cases passed again. Capability generation/check and diff whitespace checks passed. See [partial update contract](character-import.md#partial-advancement-updates). These are storage and workflow checks, not proof of edition-specific advancement legality.

## Live investigation plan expansion (2026-09-16)

All 299 tests passed, including 14 new extension tests. A new seven-transition investigation replay verified immutable delivered text, no automatic discovery or hypothesis change, fresh-process recovery and restore. Action/combat/exploration walkthroughs, both twenty-turn campaign replays and eight Keeper cases passed again. Capability generation/check and diff whitespace checks passed. See [live expansion contract](investigation-runtime.md#extend-a-running-investigation). These scripted fixtures do not certify full rules coverage or live-player experience.

## Autonomous inspection, extension and replay (2026-09-16)

Three passes completed: strengthened exploration snapshot validation; added isolated previews and pending reminder rescheduling; verified the combined workflow with an eight-transition cross-process replay. All 285 tests passed (12 new tests beyond the prior 273), plus action/combat replays, both twenty-turn campaign replays and eight Keeper cases. Capability generation/check and diff whitespace checks passed. The new exploration replay reached minute 12 with supplies exactly zero, recovered a due reminder in a new process, and verified no preview mutation or duplicate spending. See [iteration record](iteration-2026-09-16.md).

## Exploration time and supply accounting (2026-09-16)

All 273 tests passed, including 18 new exploration tests covering atomic costs/time, retry, deadline boundaries, recurring catch-up, action settlement, encounter guards, reserved resources, private cold recovery and restore. Action/combat walkthroughs, both twenty-turn campaign replays and eight Keeper cases passed again. Capability generation/check and diff whitespace checks passed. See [exploration scope and commands](exploration.md). Automated checks do not certify system-specific travel or rest rulings, or live-player experience.

## Live investigation knowledge (2026-09-16)

All 255 tests passed, including 13 new runtime investigation tests for split knowledge, private verdicts, dependency analysis, atomic acquisition, cold recovery and restore. Action/combat walkthroughs, both twenty-turn campaign replays and eight Keeper cases passed again. Capability generation and diff whitespace checks passed. See [runtime scope and commands](investigation-runtime.md). These are automated and scripted checks, not semantic proof or live-player evaluation.

## Structured campaign characters (2026-09-16)

All 242 tests passed, including 18 new character import tests. The action/combat walkthroughs, both twenty-turn campaign replays and eight Keeper cases passed again. Capability generation and diff whitespace checks passed. See [character import](character-import.md) for the original JSON example and private preview/apply workflow. This verifies structure and state compatibility, not full character legality or live-player experience.

## Dynamic encounter order (2026-09-16)

All 224 tests passed, including 15 new tests for joining/leaving, reorder eligibility, dependent effects, retry/rollback, cold recovery, schema 1 compatibility and branch restore. The combat and action walkthroughs, both twenty-turn campaign replays and eight Keeper cases passed again. Capability generation and diff whitespace checks passed. These are automated checks, not live-player evaluation.

## Reservations and encounter boundaries (2026-09-16)

All 209 tests passed, including 20 additional reservation/timing tests. The ten-transition combat walkthrough and the five-transition action walkthrough passed with actual OS randomness, scripted choices and cold recovery. Both CoC/D&D twenty-turn replays and all eight Keeper cases passed again. Capability generation and diff whitespace checks passed. See [combat timing](combat-timing.md) for scope and reproduction.

## Recoverable action workflow (2026-09-16)

All 189 tests passed, including 20 new action workflow tests. The new five-transition walkthrough passed with actual OS dice, scripted choices, read-only Dice receipt import, fresh-process recovery during a pending choice, idempotent retries and audience-filtered output. Both twenty-turn CoC/D&D replays and all eight Keeper cases passed again. See [action workflow scope and reproduction](action-workflow.md). This is simulated acceptance, not live-player evaluation or full rules automation.

## Review defect fixes (2026-09-16)

All 169 tests passed, including 14 new regression tests for the twelve reviewed defects, legacy review migration and source changes before index rebuilding. Both twenty-turn campaign replays and all eight Keeper cases passed again. Capability generation checks passed. See [fixes and compatibility notes](review-fixes-2026-09-16.md).

## Current local tabletop interface verification (2026-09-16)

The full suite passed 155 tests using Python 3.14.7. Coverage includes removal of obsolete interaction commands without state changes, database-free topic help, help/catalog consistency, Keeper-only settings, malformed-setting rollback, compatibility with stored draw toggles, and disabled-deck aliases rejected before RNG use. Existing dice evidence, replay, private output and log tests remain passing.

Both twenty-turn CoC and D&D scripted acceptance replays passed, including cold recovery at turn ten (final HP 8 and 12). Capability generation and diff whitespace checks passed. These are automated and simulated checks, not live-player evaluation. Earlier verification records below describe previous development stages.

## Local services release verification (2026-09-16)

Earlier local-services suite: 153 tests passed in the bundled dependency environment. Seven new integration tests cover opt-in private replies, explicit published snapshots, timer ownership/acknowledgement/cancellation, foreground waiting with private UTF-8 output, weighted nested deck receipts, cyclic/missing-reference rejection, and replay without rerolling. Existing flat decks and old timer records remain readable. A regression in the new reply audience hook treated list-valued initiative results as dictionaries; an explicit type guard fixed it and the full suite passed afterward.

A separate 15-operation local walkthrough passed with actual OS randomness and an actual timer deadline. It exercised public reply publication, nested draws, private timed delivery, acknowledgement and exclusion from another player's log. Both existing twenty-turn CoC/D&D scripted replays and all eight Keeper situation cases passed again with cold recovery. Scripted replays are not live players. No external chat platform, native DLL, historical script host or offline notification service was executed.

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

## Dicebot and card-registration verification

The expanded suite passed all 126 tests. Eight new tests cover registration/aliases, atomic failed edits, table/player isolation, export roundtrip, retries without rerolling, stale revisions, bonus/penalty00 handling, refused unsupported commands and cold-process readback. A separate 20-command synthetic-card walkthrough passed with a fresh-process read after command10 and identical replay of every operation ID; its rolls came from the actual local RNG. This is command-workflow acceptance, not 20 player turns or a live external-bot integration test.

## Attribute-generation verification (2026-09-15)

All 130 tests passed using the bundled Python runtime with document dependencies. Four new tests check minimum/maximum attribute formulas and raw dice, totals with/without luck, invalid counts without RNG/state changes, five-candidate retries without rerolling, persisted batch retrieval, owner isolation, explicit selection, refusal to overwrite cards, and preservation of originals after stat edits. Fixtures use mocked dice; they are not player rolls. The initial PATH Python run lacked openpyxl for two pre-existing spreadsheet tests; the complete dependency environment passed both. Age adjustments remain a sourced guided workflow, not automated generation.

## Local Dice! adaptation verification (2026-09-16)

All146 tests passed in the bundled Python environment. Sixteen new tests cover expression/keep/fudge/percentile/pool boundaries, atomic team updates, roles, named cards/copies/bindings, core vs house checks, SAN fumble/bout handling, approved development, hidden-output suppression, private log filtering, cross-table membership, DOCX/XML and OOC exports, sourced dataset profiles, presentation switches, and creation batches. Fixed during validation: a SQLite read connection was not closed on Windows; the broad `.st` parser incorrectly captured `.strRoll`.

A separate33-command workflow used actual OS RNG with synthetic actors; every successful operation was replayed identically without rerolling. A fresh process recovered state after command17. Another player did not receive the private check in their log. txt/clean-txt/html/json/docx exports passed content and UTF-8 readback; DOCX packaging/XML was checked, not visually rendered in Word. Upstream source snapshots matched their pinned SHA-256 manifest. The tested runtime uses the Python arithmetic adaptation and local storage. See the current local command guide for supported behavior.

## Keeper Tips integration verification (2026-09-16)

493 source advice bullets are individually mapped, excluding headings and attaching cross-page continuations to their starting bullet. Front matter, translator notes and the blank last page are accounted for separately. Paragraph extraction and a rendered SAN page were reviewed; the private source audit retains the original page text. The distributed skill contains editorial topic labels, decisions, procedures and original examples, not the translated book.

Run `python -X utf8 scripts/replay_keeper_acceptance.py --output <new-private-directory>` for eight original synthetic situations: missed clue, wrong theory, split party, quiet participant, absence, closing time, rule dispute and unreadable handout. All eight passed. Each case applies a sourced event, cold-reads in a new process, retries without duplicate changes, preserves unrelated pending/private state and resource totals, and checks audience projections. Extra checks distinguish available evidence from acquired knowledge, reject profile conflicts and reject a GM-only handout variant. The readable fallback roundtrips Chinese text. Its readability problem is simulated; no visual design quality is certified by the plain-text fixture.

The worked responses were manually reviewed against the procedure's next action and invariants. They are prewritten cases, not autonomous-model performance measurements or live-player sessions. No dice or new mechanics are needed. Existing targeted suites passed 44 tests: session 24, review 4, investigation 6 and corpus/handouts 10. Full unrelated mechanics suites were not rerun for this documentation extension. Capability generation, skill metadata, reference links/anchors, UTF-8 readback and diff whitespace checks passed.

Editorial corrections made during integration: denied prior narration became a preserved perception; conflicting map/SAN presentation advice became conditional choices; default point grants and dream resets became disabled proposals; p. 36 duration advice was separated from the official rounds/hours distinction; outdated resource-rights statements remain case-specific verification tasks. No new runtime regression was found in the targeted checks.
