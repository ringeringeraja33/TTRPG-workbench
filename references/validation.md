# Current verification

## Local services release verification (2026-09-16)

Latest complete suite: 153 tests passed in the bundled dependency environment. Seven new integration tests cover opt-in private replies, explicit published snapshots, join/leave welcome events, timer ownership/acknowledgement/cancellation, foreground waiting with private UTF-8 output, weighted nested deck receipts, cyclic/missing-reference rejection, and replay without rerolling. Existing flat decks and old timer records remain readable. A regression in the new reply audience hook treated list-valued initiative results as dictionaries; an explicit type guard fixed it and the full suite passed afterward.

A separate 15-operation local walkthrough passed with actual OS randomness and an actual timer deadline. It exercised welcome, public reply publication, nested draws, private timed delivery, acknowledgement and exclusion from another player's log. Both existing twenty-turn CoC/D&D scripted replays and all eight Keeper situation cases passed again with cold recovery. Scripted replays are not live players. No external chat platform, native DLL, historical script host or offline notification service was executed.

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

A separate33-command workflow used actual OS RNG with synthetic actors; every successful operation was replayed identically without rerolling. A fresh process recovered state after command17. Another player did not receive the private check in their log. txt/clean-txt/html/json/docx exports passed content and UTF-8 readback; DOCX packaging/XML was checked, not visually rendered in Word. Upstream source snapshots matched their pinned SHA-256 manifest. No native Dice! DLL, live QQ group, full historical plugin/template interpreter, Tower cloud or complete129-command compatibility is claimed. See the manual coverage matrix for exact remaining gaps.

## Keeper Tips integration verification (2026-09-16)

493 source advice bullets are individually mapped, excluding headings and attaching cross-page continuations to their starting bullet. Front matter, translator notes and the blank last page are accounted for separately. Paragraph extraction and a rendered SAN page were reviewed; the private source audit retains the original page text. The distributed skill contains editorial topic labels, decisions, procedures and original examples, not the translated book.

Run `python -X utf8 scripts/replay_keeper_acceptance.py --output <new-private-directory>` for eight original synthetic situations: missed clue, wrong theory, split party, quiet participant, absence, closing time, rule dispute and unreadable handout. All eight passed. Each case applies a sourced event, cold-reads in a new process, retries without duplicate changes, preserves unrelated pending/private state and resource totals, and checks audience projections. Extra checks distinguish available evidence from acquired knowledge, reject profile conflicts and reject a GM-only handout variant. The readable fallback roundtrips Chinese text. Its readability problem is simulated; no visual design quality is certified by the plain-text fixture.

The worked responses were manually reviewed against the procedure's next action and invariants. They are prewritten cases, not autonomous-model performance measurements or live-player sessions. No dice or new mechanics are needed. Existing targeted suites passed 44 tests: session 24, review 4, investigation 6 and corpus/handouts 10. Full unrelated mechanics suites were not rerun for this documentation extension. Capability generation, skill metadata, reference links/anchors, UTF-8 readback and diff whitespace checks passed.

Editorial corrections made during integration: denied prior narration became a preserved perception; conflicting map/SAN presentation advice became conditional choices; default point grants and dream resets became disabled proposals; p. 36 duration advice was separated from the official rounds/hours distinction; outdated resource-rights statements remain case-specific verification tasks. No new runtime regression was found in the targeted checks.
