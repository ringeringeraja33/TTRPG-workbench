# Upstream adoption and evidence

Reviewed snapshots on 2026-09-06. These are selected source reviews, not execution of all upstream test suites. Public availability does not establish correctness or license compatibility.

| Upstream / pinned revision | Files inspected | Adopted here | Acceptance / remaining boundary |
|---|---|---|---|
| [gm-apprentice](https://github.com/AntTheLimey/gm-apprentice) `b9912ea` | `skills/session-prep/SKILL.md`, `skills/ttrpg-expert/systems/coc-7e/combat-reference.md`, `tests/test_plan_leads_to.py` | Licensed lifecycle adaptation, system/topic routing and original graph auditor | `test_campaign_check.py`; CoC tied melee corrected against official rules rather than copied |
| [claude-dnd-skill](https://github.com/neuralinitiative/claude-dnd-skill) `ec072ba` | `skills/dnd/scripts/autosave_checkpoint.py`, `combat.py`, `tests/test_autosave_checkpoint.py` | Independently implemented transaction saves and explicit edition lock; no AGPL code copied | Cold recovery at turn 10; full upstream spell automation not imported |
| [coc-kp-host](https://github.com/SumanasJ/coc-kp-host) `9fedf60` | `SKILL.md`, `references/prep_persistence.md`, `carry_audit.md`, `scripts/roll.py` | MIT-attributed preparation adaptation, separate player/GM records and inventory checks | Audience projection and split-party tests; OCR limitations remain explicit |
| [SagaSmith D&D](https://github.com/SagaSmithAI/Sagasmith-dnd) `065ec82` | `packages/domain/src/sagasmith_dnd/resources.py`, `packages/mcp/tests/test_session_exposure.py`, `test_stable_recovery_mcp.py` | Unmodified Apache-2.0 resource module vendored in `scripts/vendor`; finite-resource wrapper in ledger | Upgrade with spent resources, duplicate replay and restore tests; not a complete D&D engine |
| [RePoG](https://github.com/tritonsan/RePoG) `92eef59` | `tools/rpg_state.py`, `check_state.py`, `tests/test_hosted_runtime.py` | Original implementation of operation identity, revision validation, append-only restoration and invariant checks | Concurrent writer, atomic failure and idempotence tests; no hosted runtime imported |

## Forum questions converted to tests

- [BRP firearm rate discussion](https://basicroleplaying.org/topic/18539-firearms-questions-12-or-13-how-does-it-work/): distinguish fractional weapon rates from multi-shot and full-auto modes. Consult the weapon entry rather than treating a fraction as a chance to hit. Automatic fire details were checked in the local CoC7 rulebook, PDF 99–100.
- [2024 spell discussion](https://www.reddit.com/r/onednd/comments/1f8nnon/so_casting_multiple_spells_in_a_turn_got/): slot expenditure is per turn, including reactions during that turn. Verified against SRD 5.2.1 PDF 105; tested same-turn rejection and a different actor's turn.
- [Fate solo-play discussion](https://forum.rpg.net/index.php?threads/fate-condensed-actual-solo-play-testing-the-system-to-the-limit.928312/): useful as an example of a declared oracle overlay, not a canonical rules test. Downloaded and inspected public HTML; do not copy its story or infer that every displayed character is a valid standard build. Consequence and advancement checks use Fate SRD.

Private research records retain URLs, download status, SHA-256 hashes and extracted text. The BRP page was readable through web search but direct download returned 403; no authentication bypass was attempted. Official Blades player kit and Pelgrane's condensed Trail rules were downloaded; acquisition alone does not count as complete rule validation. See [advanced mechanics](systems/advanced-mechanics.md) for verified additions.

## Language decision

Use English for the skill entry, new reusable workflows and code documentation. Preserve Chinese user interaction, translated source titles and existing Chinese rule-reference material. English simplifies alignment with the predominantly English upstream APIs and rule terms; no comparative model evaluation has demonstrated that translating the entire library improves GM quality. This release does not claim such evidence.
