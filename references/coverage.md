# Current capability coverage

Generated from `capabilities.json` by `scripts/capabilities.py`. Edit the JSON, then regenerate.

Statuses are scoped claims: supported, partial, none, or not-applicable. Source access, retrieval, procedures, arithmetic and interaction checks are independent. No row certifies an entire system.

| Capability | Source | Retrieval | Procedure | Arithmetic | Interaction | Scope and limits |
|---|---|---|---|---|---|---|
| [CoC7 core and table procedures](systems/coc7-table.md) | supported | partial | supported | partial | partial | Core creation, combat, SAN, chase and growth procedures; worked journalist and simulated replay. Not all occupations, monsters or exceptions. |
| [CoC7 automatic fire, vehicles and rituals](systems/coc-vehicles-rituals.md) | supported | partial | supported | partial | partial | Sourced bounded helpers; consult advanced-mechanics.md for volleys. Fractional-Build vehicles and source-specific exceptions remain source-dependent. |
| [D&D SRD 5.2.1 core](systems/dnd2024-table.md) | supported | partial | supported | partial | partial | Core table procedures, Fighter build and advancement examples, ledger replay. Does not include non-SRD books. |
| [SRD classes and spells](systems/dnd-class-spell-package.md) | supported | supported | partial | partial | partial | Source-bound reader covers 12 class ranges and 339 spell entries when the verified PDF is available. Multiclass slots, fixed HP and Counterspell helpers; not every class/spell interaction. |
| [Trail of Cthulhu](systems/trail-of-cthulhu.md) | supported | partial | partial | partial | partial | Creation, pools and investigation procedures; source-specific safe-rest and psychotherapy helpers in corpus-adapters.md. No full campaign certification. |
| [City of Mist v0.75 quickstart](systems/city-of-mist.md) | supported | partial | partial | none | partial | Quickstart moves, tags and statuses; full theme questionnaires and long-term advancement are outside this source. |
| [Fate Condensed](systems/fate-blades-procedures.md) | supported | partial | partial | partial | partial | Creation, actions and aspects; bounded consequence absorption/recovery helpers. No exhaustive stunt or campaign validation. |
| [Blades in the Dark](systems/blades.md) | supported | partial | partial | partial | partial | Core actions/resistance and bounded vice/downtime helpers. Full crew, trauma and flashback interactions remain uncovered. |
| [Local homebrew adapters](systems/local-homebrew.md) | partial | partial | partial | partial | partial | Edition-bound interfaces and selected local_rules.py operations. No complete GugDove, Jiangshan or other homebrew engine. |
| [Other systems and older editions](systems/corpus-adapters.md) | partial | partial | partial | none | none | BRP, older D&D, Pathfinder, Warhammer and other materials require source-specific edition and topic checks. Extraction is not rule verification. |
| [Optional corpus and handout processing](corpus-use.md) | not-applicable | supported | supported | not-applicable | partial | PDF, scan/OCR, CHM and old DOC adapters depend on available tools; card audit and recipient manifests. Full-text caches stay private. |
| [Historical creation and scene packs](background-design.md) | supported | partial | supported | partial | partial | Three reviewed example packs, six CoC7 builds and nine scenes; configured arithmetic does not establish historical truth or semantic clue sufficiency. |
| [Original rulebook and design lab](rulebook-authoring.md) | not-applicable | not-applicable | supported | partial | partial | Explicit manifest dependencies, conflict repair and dream-game prototype. Undeclared prose contradictions and general balance are not automatically certified. |
| [Persistent session ledger](session-runtime.md) | not-applicable | not-applicable | supported | not-applicable | supported | Atomic sourced events, revisions, replay, rollback and audience projection. Stores adjudicated outcomes, not complete action legality. |
| [Evidence dependency audit](investigation.md) | not-applicable | not-applicable | supported | not-applicable | partial | AND/OR dependencies, unseeded cycles, missing evidence, bottlenecks and split knowledge. Declared logic only; not proof of fictional persuasiveness. |
| [Branch-aware recap and next preparation](session-review.md) | not-applicable | not-applicable | supported | not-applicable | partial | Read-only current facts, active events, source revisions and explicit prep notes. No automatic inference of beliefs or triggering of GM plans. |

## Verification and history

See [current verification](validation.md) for commands and the latest executed results. Live-player evaluation is outside the requested acceptance scope. Simulated cases do not establish play quality or exhaustive interaction coverage.

Earlier coverage and acceptance records are retained in [coverage history](coverage-history.md) and [validation history](validation-history.md); historical gaps and counts are not current status.
