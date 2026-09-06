# Local corpus adapters and edition boundaries

Use these source-backed procedures within their stated scope without requiring the original collection. Source titles, editions and section/page references identify the evidence; local files and private indexes are not user requirements. For uncovered interactions, consult accessible official sources or user-supplied material. These are targeted adapters, not complete rulebook replacements. All examples below are original numerical fixtures. Paragraph numbers refer to the reviewed document edition and may differ in other layouts.

## CoC core, expansions and reference cards

The corpus contains sixth-edition material, seventh-edition core/quickstart/anniversary editions, an investigator handbook, fifth-edition Dreamlands material and a wartime investigator supplement. Freeze the core version and list every enabled supplement. A quickstart creation method cannot silently override full-book creation. A modern printed character sheet does not make modern equipment available in a 1920s scenario.

Use the existing [CoC7 procedures](coc7-procedures.md) and [vehicle/ritual package](coc-vehicles-rituals.md). Retrieve the actual occupational entry for its skill choices, Credit Rating range and point formula; record occupation points, interest points, starting percentages and experience-package changes separately. Do not enable an experience package merely because a sample workbook contains it. Compare an automatic card with both the book and independent arithmetic.

For Dreamlands or wartime play, prepare a conversion ledger: original edition, setting-specific skills, alternate identities, waking/dream states, setting resources, equipment availability and unresolved conversions. The fifth-edition Dreamlands text is not an official seventh-edition conversion. Consult the selected text before transferring sanity, travel, dream abilities or creature statistics. Wartime fiction is not historical evidence for actual technology or institutions.

KP card decks are local retrieval aids. A weapon card supplies a candidate entry to check against the selected core; a fear, event or NPC card supplies a prompt whose introduction must fit current fiction. Keep card provenance, selected result and subsequent player-visible consequences. Artifact entries need trigger, activation, cost, duration, detectable evidence, counterplay and unknown effects; never infer these from the artifact's name alone.

## Trail of Cthulhu: recovery is several procedures

Source: `TOC克苏鲁迷踪-玩家手册-数字版.pdf`, PDF63-65. Keep Health, Sanity, Stability, investigative pools and general pools separate. Existing creation/investigation procedures are in [the TOC reference](trail-of-cthulhu.md).

For a safe-haven rest, select at most three eligible general pools, establish at least one uninterrupted safe hour, and enforce once per session. Health, Sanity and Stability are excluded. Preview restoration during the rest and commit only at its conclusion, so an interruption does not require undoing unrelated spending. `local_rules.toc_safe_rest` implements this bounded operation; it does not determine whether a location is safe.

Investigative pools refresh at scenario boundaries, or the specific milestones the Keeper establishes for a multipart investigation. The physical general abilities listed on PDF64 have a 24-hour clock since their last expenditure; other general pools follow the scenario boundary. Track each pool's last spend, the scenario identity and the safe-rest use flag. Passing an in-world midnight is insufficient.

For psychoanalysis restoring Stability (PDF63), resolve the uninterrupted test first: difficulty 4, or 3 for the stated priest/alienist specialists. Spend on the test separately from the successful recovery purchase, which restores two Stability per additional pool point. Failure prevents the same analyst retrying until the patient loses more Stability. `local_rules.toc_psychotherapy` computes the costs after the fictional permission is established. Example: pool 6, test spend 2, die 2, recovery spend 3 restores 6 and leaves 1, capped at the patient's rating. This does not implement the separate temporary-lucidity procedure.

Sanity restoration depends on purist/pulp configuration, and the multi-scenario treatment on PDF65 has its own continuity conditions. Do not reset it together with ordinary pools. The source's mental-health rules are fictional game abstractions, not a clinical model.

## City of Mist quickstart 0.75

Use the [existing tag/status procedure](city-of-mist.md). The corpus gives access to all pages of the quickstart, but not a full themebook collection. Read an action's complete trigger and result options, then apply minimum results, extra options and consequences in the stated order.

PDF14 contradicts itself about whether the named upper-hand option costs or grants one Juice. Record both passages and resolve the table's interpretation before spending. Keep this as a translation/source conflict, not an implemented universal rule. PDF15 includes action-specific minimum results and downtime choices: a nonpositive Power does not by itself settle every minimum. Keep theme changes, burned tags and spectrum states separately from a numeric HP ledger.

## BRP scanned excerpt

`BRP-基础角色扮演.pdf` is a 23-page scanned extract. Its cover/printing identity remains unresolved; do not label it the current ORC edition. OCR reads its older attribute scale and percentage checks, but its two columns interleave in extraction. Verify the relevant page image before quoting a table or formula.

PDF3-5 introduce attributes, derived values and Power Points; PDF8-9 cover profession and personal skill allocation. A native attribute such as POW 12 and its POW×5 check are distinct fields. Do not store POW 60 then multiply again, or import CoC7 occupation budgets. Record exactly which optional modules the excerpt includes and which need a different book. Source-specific creation can proceed from reviewed passages; an unverified scan cannot establish full BRP coverage.

The page images for PDF8-9 were checked: this excerpt allocates 300 profession points, added to skill bases, and INT×10 personal points. A GM-approved custom profession selects ten skills. The GM may impose a 75% starting cap, with the stated exception for a base already higher than75; this is a table option to record, not an unconditional global cap. Example: INT12 gives a separate120-point personal budget, so a character must account for both300 and120 rather than spend420 freely as profession points. Record each skill's base, profession spend, personal spend and final percentage, then verify equipment against profession, period, skill and status. Printed pages on these two images are11-12; do not transfer this offset to another file.

## Pathfinder CHM and WFRP4 CHM

The Pathfinder filename `v2.01` is an archive revision. Its “探索者协会PFS索引贴” bibliography identifies the CRB by PZO1110 and lists the older supplement family; its “CRB 核心规则手册” spell chapter uses standard-action casting. Treat this as a PF1-era compilation, not PF2 Remaster. Its pages mix books, variants and organized-play material: choose allowed books and whether PFS restrictions apply before constructing a character.

Operational path: bind ancestry/race and class variant, audit ability generation and level-by-level choices, then separate BAB, saves, skill ranks, class skills, feats, spell lists and casting slots. A feat catalog (“专长列表”) requires its prerequisites and source scope; a class-design chapter (“职业设计”) is guidance, not permission for an official class. Social conflicts (“社交冲突”) and downtime (“休整期活动”) can support campaign planning once their native economies are read. Do not use SRD5.2.1 multiclass arithmetic here.

The WFRP archive identifies itself internally as fourth edition. Start with the character-creation sections “种族”, “阶级与职业”, “特质”, “技能与天赋” and “角色成长”. Preserve rolled-choice XP rewards and character-creation choices. Advanced skills require training; basic skills can use the associated characteristic without advances. Career-based allowed advances and increasing XP costs make a flat point-buy allocator inappropriate.

Read the “检定” and “战斗” chapters for percentile outcomes, SL, opposed results and turn structure. The local text includes automatic success/failure and alternative options; freeze those rather than importing CoC success tiers. Record Fate/Fortune and Resilience/Resolve separately: their initial relationships do not make them a single spendable pool. Confirm the enabled Advantage rules and errata before using an online example; the local compilation has not been certified against later revisions.

## Chinese fan systems: independent profiles

| Corpus book | Confirmed operating distinction | Required state and next source read |
|---|---|---|
| 江山雪TRPG江湖篇, internal 3.1 test version | Five-element attributes, stance and action timing | Paragraphs 121-134 for HP/stance; read action timing and ability trees before selecting actions |
| 收尾人事务所 0.61 | Construction buys attributes and ranked slots; reserve/reactive actions coexist with active limits | Paragraph 321 for slot upgrades, 457/477 for combat phases/limits; track office funds, slot rank, AP, reserve and EGO separately |
| 明日方舟 1.80, Doyle.麦子 | Level returns to 1 on promotion, while cumulative advancement has its own record | Paragraphs 436 and 490-496; record rarity, promotion tier, current level, cumulative level bonus, physical and Arts defenses |
| 明日方舟 干员行动准则 0.51, Daniel 扭蛋 | Separate attribute/specialization and Arts-design system | PDF9-10 contents route to creation at PDF11+, resolution at PDF33+, combat at PDF37+; never import the 1.80 equations |
| 明日方舟·泰拉世界 | CoC-like skills plus infection and Arts procedures | PDF65 infection example; read PDF93-99 damage, combat and Arts entries; store infection components and fictional symptoms independently |
| 诡秘之主 v4.0, MrGTM | CoC7-derived SPI, overflow and digestion | PDF5-9; see [local-homebrew](local-homebrew.md); signed/overflow state cannot fit a clamped generic resource unchanged |
| 诡秘之主 扩展3.0.0内测5, 琉璃版 | D20-family checks and distinct critical damage, resources and pathways | Paragraphs 253-255 critical floor; 314/353 sanity/HP; use the specific sequence ability and prerequisites from its chapter |
| 圣杯4.2.4 / 4.2.5 | Two distinct rule files with automatic-card requirements | 4.2.5 PDF1 binds automatic card 1.76.3; master/servant/treasure profiles and source card are required for a full build |
| 龙族0.9.4.3 | Bloodline, speed/AP and powers change action and regeneration rules | Paragraphs 159/166/218/244-246; record bloodline state, focus, regeneration attempts and action transfers; reconcile general/specific costs |
| 道诡异仙 | Custom creation and finite growth/reallocation, despite familiar skill names | Paragraphs 24, 48-52, 91: audit attribute cost bands separately from initial, interest, extra and growth skill points |
| 规则怪谈TRPG, 启鸣子 | Revisable in-fiction rules, cognition and pollution | PDF3-5, 13: source leaves some allocation language nonnumeric; establish the missing table ruling before certifying a card |
| 无限流DND版1.1 | Homebrew derived HP/MP/stamina formulae | Paragraphs 4/16; do not treat the filename as an official D&D rules profile |

### Stance and ambiguous death results

Jiangshanxue paragraph 133 sends damage from a successful parry to stance, overflowing into HP; stance reaching zero clears action points for the round. Paragraph 134 restores stance when combat ends. `local_rules.jiangshan_parry` assumes the parry has already succeeded. Example: HP10, stance4, AP3 and damage7 leaves HP7/stance0/AP0; damage4 causes no HP loss but still breaks stance.

Paragraph 122 triggers below zero HP and specifies results below/above 5, plus natural20. Exactly5 is omitted. `local_rules.jiangshan_death` returns a pending ruling for5; it also asks for rounding when natural20 restores half an odd HP maximum. It does not invent a D&D-style death-save track. Zero HP does not trigger this particular passage. Record the table ruling and source discrepancy before continuing.

### Promotion and freeform ability authoring

For systems with promotion resetting a displayed level, maintain `(tier, current_level, cumulative_progress, unlocked_choices)`. Preview the tier change and rebuild every dependent value, leaving earned skills/resources intact only where the selected rule says so. Do not subtract all prior bonuses because the displayed level became1.

For a custom spell, Arts ability, EGO, bloodline power or treasure, write its permission, target, range, action cost, resource cost, prerequisites, damage/status, duration, stacking, counterplay and recovery. Compare at least one native ability of the same role and one competing role in the same version. Separate source rules from GM-approved design parameters; resemblance to the IP's fiction cannot establish numerical balance.

The helper module implements four bounded operations only. It does not roll dice, determine action legality or certify complete characters for these fan systems. For TOC's signed Health/Stability or Mysteries' overflow/signed SPI, retain explicit structured state and pending transactions until the ledger adapter supports that resource domain; do not clamp away legal negative states or overspend to simulate them.
