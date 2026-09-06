# Rulebook authoring

Use for an original TTRPG, a system adaptation, organizing notes, writing/revising chapters, reconciling contradictions, or producing a player quickstart. Read the user's actual source material before proposing the book. A chapter request does not require restarting the whole project. Use the user's language for deliverables and preserve established terminology and lore.

## Intake and authority

Record user commitments separately from provisional design decisions. Extract who plays whom, recurring player activities, meaningful choices, desired pacing, complexity, randomness, lethality, growth and session/campaign length. Turn these into observable hypotheses: e.g. two viable approaches per obstacle, no more than two lookups per action. Do not assume a combat chapter, percentiles, classes, a GM or dice are required. Mark omitted modules with reasons.

Ask only questions that would change the direction of the design. If no dice system is chosen, compare two or three candidates, including an original mechanism where useful, and proceed with a labelled reversible proposal. Preserve explicit constraints such as diceless play. User-approved canon outranks our suggestions. When two user passages conflict without a clear revision order, preserve both in the issue ledger, propose alternatives and keep the affected rule provisional; do not silently pick an authoritative version.

Read private draft sources in place. Create working derivatives in the user's private project, never inside a publicly distributable skill. Preserve originals and raw notes. Published examples must be independently invented fixtures, with synthetic input explicitly labelled. Do not transfer private lore into demonstration files.

## Research by design problem

Research actively when designing unfamiliar mechanics, selecting a base or resolving source claims. Search local material and official rules/SRDs, then designer explanations and relevant forum discussions. Read actual procedures, not just product descriptions. Compare trigger, decision authority, costs, outcomes, recovery and dependencies. Record what is adopted, rejected or transformed and why it serves this game's activities. See [research examples](rulebook-sources.md).

A forum post is a proposed interpretation or test lead. Its popularity cannot validate a rule. Separate published rules, designer commentary, design inference, adapted expression and original text. Record author/publisher, version/date, URL, page/section, access date, read scope, license and intended use. If a useful source is inaccessible, record the gap and continue original design without presenting it as an official rule. Keep full downloads and extraction caches in index_root. Before reusing text, tables, art or code, verify permission for that specific material and retain attribution; an SRD license does not automatically cover the whole book or its setting.

## Project and entry modes

Copy only needed parts of [the project template](../assets/templates/rulebook-project.md). Maintain a brief, contents, glossary, canonical rules, numeric/resource tables, character sheet, GM reference if applicable, examples, open issues, sources, dependency map and revision log. Each mechanism has a stable ID; its prose has one canonical home. Tables and cards reference its ID and revision. Keep public rules and GM secrets in separate source files, with an explicit public export list.

| Entry | First useful output | Preservation and follow-through |
|---|---|---|
| Concept only | Design brief, candidate mechanism comparison, minimum playable rules | Label assumptions; do not invent user approval |
| Scattered notes | Note-to-chapter map, glossary and playable chapter | Distinguish exact retained intent, editorial organization and added rules |
| Contradictory rules | Quoted/located conflict, reproduction, proposed resolution | Show affected chapters/cards/examples; retain unresolved alternatives |
| Expand one chapter | Complete procedures in established voice and terminology | Check its inputs and callers without redesigning unrelated systems |
| Change a mechanic | Old/new behavior with costs and migration | Update transitive dependencies, examples and quick references |
| Quickstart / assembled book | Explicitly ordered public content and necessary rules | No undefined quickstart terms or hidden exception dependencies |

## Write executable text

For every mechanism specify: ID/revision, intent, trigger, actor and decision authority, prerequisites and legal targets, inputs, ordered steps, payment timing, outcomes, duration/end, exceptions, stacking/priority, recovery and an ordinary plus a boundary example. An inapplicable field gets a short reason. Define rounding, caps, ties, simultaneous effects, cancellation/refunds and retry costs wherever they arise. Examples show full initial state, choices, inputs, calculation and final state; examples may not introduce new rules.

Describe NPC authority and player choice explicitly. Give defaults for common cases and scoped rulings for unusual ones; do not use unrestricted GM discretion to conceal an absent core procedure. Separate rules from design commentary. Teach in order: activity and sample exchange, terms, core action, creation, relevant conflicts/resources, advancement, GM/content tools, examples and reference tables. A no-combat game can handle opposition through negotiation or obstacles without inventing weapon lists.

## Revision and numerical review

For a change, list changed IDs, reverse dependencies, conflicting claims, affected tables/cards/examples and saved-character migration. Use `rulebook_check.py project.json --changed ID` on an explicit dependency manifest where maintaining it saves repeated work. The checker detects structural omissions, competing registered claims and stale bindings; it cannot read prose for contradictions or prove completeness. A clean manifest still requires reading the affected passages.

Model every resource's source, sink, bounds, transfer, refresh and exhaustion. Search for actual repeated action sequences before declaring an exploit; distinguish cost-free gain from intentionally renewable income with time/risk. Test simultaneous effects, empty/full pools, stacking, failure, interruption, invalid builds and end states. Compare strong and weak builds, cooperation and competition where relevant, one scene and an expedition. Reuse existing dice tools for supported distributions; for new mechanics use small explicit-input helpers, exact enumeration or seeded simulation with stated assumptions. Never evaluate formulas from untrusted files as code.

Probability is evidence about a model, not a balance certificate. Record success categories, costs, future opportunity loss, spotlight, lookup burden and strategic alternatives. A choice can be numerically inferior yet grant different fictional access; identify that distinction. Core revisions must update the rule, table, character sheet and example together. Do not claim every exploit is excluded by bounded tests.

## Minimum playable validation

First produce enough rules to create two distinct complete characters and resolve a short scenario without inventing rules mid-turn. Include equipment/abilities and recovery/growth, or justified omissions. Run at least 20 simulated player turns for a new minimum playable ruleset, covering the main choices, failures and consequences, resource exhaustion/recovery, end-of-scene and expedition resolution. Use declared simulated rolls; do not claim real-player testing. A small editorial update needs only relevant checks, not another full replay.

Keep the trace (initial state, declared action, rule revision, input, calculation, final state), error/fix ledger and recheck result. Save and reload mid-scenario when persistent state is part of the prototype. Test missing rules and changed versions explicitly. Unresolved material rules leave the affected build provisional. A model can pass deterministic checks while strategy, pacing or long campaigns remain untested. Live-player evaluation is outside this project's acceptance scope and is not a blocker.

The [three authoring cases](../assets/examples/rulebook/index.md) demonstrate concept, note organization and conflict repair. The dream prototype supplies two cards and a reproducible 20-turn trace. Its helper implements only its named original rules, never a universal engine for user games. Finish each task with changed artifacts, validated behavior, remaining decisions and the next usable writing entry point; do not substitute a chapter count for playability.
