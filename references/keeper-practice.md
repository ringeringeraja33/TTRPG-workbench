# Keeper practice: decisions and recovery

Use for investigation stalls, horror pacing, participation, absence and handout preparation. These independently written procedures synthesize the multi-contributor *Keeper Tips* (Chaosium; Mike Mason introduction, 2021), Chinese translation 古早茶 (preface 2023-12-27). All source pages refer to the supplied 50-page translated PDF. Opinions are not edition rules. The [item audit](keeper-tips-adoption.md) records every bullet and continuation; the source PDF is not required to use this skill.

Read the relevant procedure, use the [working sheet](../assets/templates/keeper-session.md), and compare the [eight cases](../assets/examples/keeper-practice-cases.json). Preparation is GM-only; publish a separately reviewed player view.

## Z - Table agreement

**When:** new group, changed tone, content boundary or access difficulty. Sources: pp. 5-8, 12-16, 34, 43, 48.

Record edition, horror style, end time/breaks, dice controller, private delivery, character-conflict boundaries, attendance threshold and absent-character policy. Reuse existing decisions. Invite preferences for speaking, writing, observing, explicit options or passing; do not infer them from appearance or silence. Offer plain text and a simple pause/omit signal. Save the agreed boundary, not personal reasons or trauma histories.

Discuss whether historical prejudice belongs in this game; provide context without treating stereotypes as research. A genre agreement does not authorize every shock. On a boundary change, pause the affected detail, omit or revise it and resume from an agreed situation without penalizing the player. Keeper enjoyment and access needs count too. Prior module knowledge is not an automatic exclusion: agree how to separate spoilers or choose another scenario. Phones, lighting, refreshments, cameras, group size and session length remain table choices.

**Save/check:** `keeper.agreement`, preferences and revised boundaries; verify the next scene and each player's participation route fit them.

## C - Character coverage and continuity

**When:** creation, pregens, a newcomer, absence or replacement. Sources: pp. 8-15, 19-20, 23, 28, 31-32, 40-41, 48.

List scenario tasks against actual skills, languages, equipment and contacts. Distinguish required access from optional advantages. Repair an uncovered requirement with a plausible alternate method, reachable specialist or changed premise before play; never silently grant points. Give unusual existing skills a consequential opportunity without guaranteeing success.

For each character record a reason to participate, a valued connection and an offered scene opportunity. Optional prompts: ally, neutral acquaintance, rival. Check agreement before turning a loved one into a victim or traitor. Introduce potential replacement NPCs before they are needed. Their player card contains only their knowledge, not the GM explanation.

On absence use the agreed safe fade, bounded authorized proxy, side session or pause. Preserve inventory, SAN and unresolved choices; absence alone does not justify death or spending. Recheck attendance and task coverage. A returning character learns information through a recorded exchange or agreed recap. A replacement never inherits all party knowledge automatically.

**Save/check:** `keeper.coverage`, `keeper.attendance`, controller and return point; character hooks under `private.review.character_hooks`. Confirm an absent specialist does not remove every route and the original character can return without invented actions.

## D - Scenario frame and revision

**When:** design, review, reskin or compression. Sources: pp. 8-10, 17-23, 25-32, 37-39.

Write antagonist goal, resources, necessary steps, trigger times and responses to interference. Separate actual events from conditional plans. State consequences of inaction and evidence revealing their causes. Use [adventures](adventures.md) and [investigation audit](investigation.md) for scene access and conclusion routes. Include noncombat approaches, withdrawal and a consequential ending choice where the premise allows. A specialist provides access or expertise while players retain the decisive choice.

A bounded convention scenario can limit geography and duration while preserving method, order and outcome choices. Do not prescribe player actions. Identify optional scenes that can be removed without losing necessary evidence. Link campaign episodes through consequences and recurring people. Use a short public premise and a separate causal GM frame.

For era changes audit transport, communication, institutions, equipment and clue access with [background design](background-design.md). Phones and authorities work within established capabilities; outages or obstruction need a cause and observable limits. Do not disable a sensible solution solely because it bypasses a scene. Consequences follow witnesses, evidence and motives, not a moral punishment schedule.

Keep ideas in the user's project; discard or save those that do not serve this scenario. A film's predetermined reveal is inspiration, not a player script. Review written instructions from a recipient's perspective and record trigger, defect and repair. External playtesting or community sharing requires the user's scope and is not a completion gate here.

**Save/check:** `keeper.design`, conditional plans in `private.review.gm_plans`; test refusal, missed evidence, negotiation and withdrawal against coherent next states.

## I - Stalled investigations and red herrings

**When:** no informed next choice, missed clue or repeated unsupported theory. Sources: pp. 6, 13-15, 17-22, 24-25, 29-31, 41.

1. Ask for the current goal and supporting evidence; compare with information actually delivered. A recap records interpretation, not a change to world truth.
2. Diagnose inaccessible evidence, insufficient evidence, overlooked information, mistaken inference, unclear affordance, missing skill, fatigue or preference mismatch.
3. Match the response: neutrally re-present a delivered fact; clarify an observable exit; offer a genuinely independent acquisition route; point to a known specialist; or offer a break. An explicit inspection of an accessible hiding place can reveal its contents when no uncertainty remains under the selected procedure. A failed roll retains its announced consequence; alternatives have their own requirements.
4. For a false lead define disconfirming evidence, how it can be obtained and reasonable checking time. When exhausted, state the dead end and remaining known leads. Do not keep adding suspicious details or claim all evidence has been found when some remains.
5. Offer choices without naming the culprit or confirming guesses. An unresolved mystery is a valid outcome. If the group prefers character competence over player puzzles, use the system's check or an agreed explanatory shortcut, labelled appropriately.

**Example:** a destroyed shipping register has a previously established customs duplicate. Offer a way to learn of and request the duplicate; do not teleport the destroyed original into the next room.

**Save/check:** diagnosis, delivered evidence IDs, theory and disconfirmation, offered routes and next choice. Theories belong in `private.review.player_hypotheses`. Audit separated parties individually; graph support does not prove a deduction's semantic truth.

## T - Truth, perception and improvisation

**When:** relocating evidence, adopting player ideas, delusions or corrections. Sources: pp. 8-10, 12, 14, 24-25, 27, 29-30, 35-38.

Keep established facts, uncommitted alternatives, character perceptions and player hypotheses separate. Preserve the exact disclosed observation and recipients. Mark its nature in the GM record even if the character does not know it.

Fill an uncommitted gap only when the addition fits established causes, timing, access and evidence. Before moving a clue check origin, transport and whether its location was established. Prefer distinct corroboration to relocating a unique object. Log the reason and preparation revision. A theory may inspire a future uncommitted event; it cannot retroactively change a culprit fixed by dependent evidence. An agreed collaborative mystery must identify co-authored truths before play.

Do not deny having described something. Say “You saw a face a moment ago; the window is empty now.” Preserve the observation separately from whether someone was physically there. A bookkeeping mistake requires a disclosed correction, not an invented hallucination. Rewinds require agreement and a new restore event retaining old history. A dream reset is a house-rule proposal, not a silent rollback.

Cinematic mood does not grant character knowledge. A summary can replace acted repetition only after actual communication is possible and agreed; it does not bypass separation.

**Save/check:** `keeper.perceptions`, `keeper.revisions` and audience-labelled facts. Recovery preserves the original observation; another player cannot see its secret explanation.

## S - Spotlight and split scenes

**When:** dominance, hesitation, separated groups or multiple speakers. Sources: pp. 12-15, 25-26, 28-32, 40-43.

Read participation preferences. Offer a concrete opening: a known contact addressing that character, an inspectable object or a text response. Allow passing. Do not force acting, public reading or personal disclosure. Helpers must not choose a newcomer's action. Explain methods and stakes, then wait for the player's choice.

Track each group's location, members, fictional time, pending intent, last opportunity and next cut. Switch after a decision or short unresolved beat; finish and save an ongoing resolution first. A 3-5 minute real-time check-in is an optional planning example, not a rule. Adjust to the table and avoid unexplained fictional time leads. Preserve separate knowledge and communication constraints; do not force separation merely to create danger.

**Save/check:** `keeper.spotlight`, `keeper.groups`, `private.next_actor` and pending intent. Both groups have actionable next beats after recovery; no silent player's action was invented.

## P - Time budget, breaks and ending

**When:** overhead, slow pacing, fixed finish or wrap-up. Sources: pp. 5, 18, 20-22, 24-32, 43, 48.

Track wall time separately from fictional minutes and rounds. The source's 30-minute closing reminder and 20-30% online overhead are suggestions, not measured universal requirements. An original 150-minute budget: 10 setup/recap, 25 orientation, 35 inquiry, 10 break, 25 escalation, 25 decision, 10 handoff, 10 technical reserve. Adjust from actual delays.

At the closure reserve, remove optional repetition or summarize agreed travel. Preserve necessary evidence, consequences and the final meaningful choice. If it cannot fit, stop at a pending choice rather than forcing success or death. Signal observable fictional deadlines; a real-world break does not advance the antagonist's clock.

Alternate tension with mundane life or rest. Laughter is not failed horror. Invite optional epilogues and next-session intentions. Save discoveries, resources, conditions and pending rules; offer a brief tone/access debrief. Keep an epilogue wish distinct from a resolved event.

**Save/check:** `keeper.budget`, cut list, stopping node and next opportunity. [Review](session-review.md) must resume the unresolved choice without invented endings or skipped costs.

## R - Rulings and conflicting techniques

**When:** uncertain rule, exception, spatial dispute or presentation conflict. Sources: pp. 5, 13, 24-31, 34, 36.

Use the locked edition/options. Establish possibility before uncertainty and stakes. Random choices may resolve genuinely undetermined details under the dice agreement; they cannot rewrite facts, enable impossible actions or override established target priorities. Do not fudge or reroll for drama.

Time-box lookups under the session agreement. If unresolved, record the exact question, missing source and affected action/resource. Continue independent action. A reversible provisional ruling needs a label, scope, agreement and review point. Keep irreversible or unsourced resource consequences pending. Apply the same ruling consistently until reviewed.

Use a simple sketch when distance, exits or cover affect decisions; pure description works for clear simple geometry. Clarify disagreements without changing established positions. End-of-round narration can summarize results but cannot withhold consequences needed for intervening decisions.

For SAN presentation, choose a brief perceptual cue before resolution and fuller description afterward, or the agreed mechanics-first form. Both retain the same stimulus, loss expression and chronology. Do not change mechanics after seeing dice.

**Save/check:** pending question and `keeper.rulings` with status/source/review point. Numeric variants use B. Profile conflicts must be rejected and pending consequences left uncharged.

## H - Horror, sanity and mythos

**When:** threat design, reveal or uncanny perception. Sources: pp. 5, 24-38, 42.

Sequence an ordinary anchor, anomaly, corroboration, actionable threat, reveal and relief. Each beat specifies perception, possible interpretation, available choice and escalation trigger. Use concrete sensory details without a mandatory sense count. Keep speech/text accessible. Hiding taxonomy must not conceal perceptible danger or nullify successful identification.

**Original example:** a station clock loses a minute; wet footprints cross a locked platform; a bell sounds under the boards; something lifts a plank. Characters may inspect, warn the porter, secure an exit or leave. The threat seeks its stolen nest and retreats when it is returned. Its reveal confirms behavior, not inevitable combat. A tea-room recovery beat remains possible after escape.

Bind a SAN stimulus to its source/edition, loss expression, prior exposure, current SAN, bout state and actual dice. Apply the selected procedure once. Narrative fear is not an extra deduction. Respect player agency except a bounded, resolved rules effect; do not use a player's real vulnerabilities as surprise material.

The official [Chaosium SAN overview](https://callofcthulhuwiki.chaosium.com/rules/sanity.html), checked 2026-09-16, separates temporary insanity lasting 1D10 hours from real-time bouts lasting 1D10 rounds. The source p. 36's interchangeable minutes/seconds is therefore not adopted as CoC7 RAW. The overview is abbreviated; indefinite recovery, summary bouts and specific tomes require the full selected edition. Travel does not establish automatic recovery. See V.

Mythos presentation may vary while rules and disclosed facts stay stable. An altered name/appearance does not automatically change a stat block. Changed powers, rewards, costs or lasting corruption require an explicit original design or house rule.

**Save/check:** `keeper.horror`, perceptions, resolved stimulus and next beat. Keep numeric timers in existing authoritative fields; do not charge again or dictate a player's feelings.

## N - NPCs and monsters

**When:** improvisation, recurring people, specialists, replacements or threats. Sources: pp. 8-10, 19, 25-26, 38-42.

Prepare a small period-appropriate roster. Each card has name/pronouns, observable trait, goal, leverage, actual knowledge and its source, false belief, availability, current activity, pressure response, negotiation/retreat trigger and player-facing text. Description can replace accents. Give bystanders mundane reasons to be present so improvised hesitation does not imply guilt.

Ask for social approach, not an acting audition: a summary of tone and leverage suffices. Map to the edition's skill/opposition. Allies can listen, clarify their own knowledge or help without solving the mystery. Betrayal requires consistent motives and prior facts; it cannot erase a well-supported discovery. Consequences of violence arise from people and evidence.

For monsters add recurring signs, movement, objective, detection limits, identification evidence, warnings and escape routes. Unusual goals may support negotiation. Award the actual result of eligible identification. Source stat blocks or label and audit homebrew. A replacement player receives a separate reviewed card without GM secrets.

**Save/check:** `keeper.cast`, audience-labelled facts and existing authoritative actor resources. NPC answers respect knowledge boundaries; withdrawal follows motive.

## M - Handouts and online delivery

**When:** text, image, audio, map, portrait or period prop. Sources: pp. 8-10, 24-27, 40, 43-49.

Use [the handout manifest](corpus-preparation.md). Record in-world creation date/condition, source/rights, player title, inspected variant, content, trigger, recipients, readable text equivalent and release state. Separate in-world artifacts from explanatory player maps. A newspaper newly printed in the scenario's 1920s need not look a century old. Research appropriate layout; current photos do not prove period conditions.

Preflight the actual recipient view: size, contrast, crop, map keys, filenames, transcript and volume. Lighting/audio remain optional and usable. If styling fails, deliver the same authorized evidence as plain text. Have a local backup; cloud accounts or purchases are not prerequisites.

Release after trigger and recipients are established. Save delivery and ownership separately: holding a prop does not make its contents common knowledge. Preserve raw logs and separate recaps. Off-session messages can be drafted locally; external delivery, extra performers, calls and recording require the user's authorization.

Check the chosen asset's actual license and attribution. The p. 49 historical public-domain cutoff and blanket image-rights claims are not current legal guidance. Named websites are discovery leads, not verified licenses or guaranteed availability. Craft, purchases and special venues are optional; simple paper or digital equivalents suffice.

**Save/check:** manifest, text fallback and release event in `keeper.handouts`; verify readable evidence and absence of hidden variants or notes.

## B - House-rule candidates, disabled by default

These proposals do not configure `dicebot.py`, `dice_local.py` or attribute generators.

| Candidate | Source | Required decision |
|---|---|---|
| Extra skill points | p. 10 bullet 1 | Pool, permitted skills, caps, stacking and balance; suggested 50-100 is not a default. |
| Minimum rolled Luck | pp. 10-11 bullet 10 | Floor, eligibility and original versus adjusted values; retain raw dice. |
| Delayed points | p. 13 bullet 5; p. 28 bullet 13 | Reserved budget, allocation deadline and caps; no retrospective allocation after failure. |
| Dream reset | p. 27 bullet 4 | Define carried knowledge/resources before play; no selective silent rollback. |
| SAN reaction/duration/recovery changes | p. 36 bullets 1, 7, 9, 11 | Separate portrayal from altered mechanics; verify RAW and record exact timer units. |
| Growth, injury, reward or corruption changes | pp. 24, 26, 29, 31-32, 38, 42 | Identify exact rule and actor; pacing alone grants no stats or damage. |

Each proposal records ID, base profile, source suggestion, exact change, status/consent, effective point and reversal plan. Accepted changes enter an explicitly reviewed profile and character/resource operation. Unresolved proposals remain preparation, not apparently enforced runtime options. `session.py` rejects in-place profile changes: preserve the old ledger and create an explicitly reviewed new state if profiles change; no automatic migration is implied. Card commands store values but do not certify point-buy legality.

## V - Rule and resource verification queue

For each claim record edition, missing rule, selected source, confirmed result and decision. The checked duration discrepancy is in H; these cases remain conditional:

- P. 36: ending a bout, temporary duration, indefinite recovery and SAN restoration are distinct. Travel alone resolves none of the missing treatment details. Consult the selected core Sanity chapter for the actual case.
- Pp. 31-32, 37-39: distinguish locating a passage, initial reading, full study, Mythos Rating and learning a spell. Identify book, language, access and phase before advancing time or knowledge. [Ritual procedures](systems/coc-vehicles-rituals.md) cover bounded spell learning, not every tome.
- Pp. 24-26, 29, 32, 34, 36, 38, 41: skill scope, automatic growth, pushed consequences, unexpected equipment, involuntary actions and SAN rewards require matching rules or an explicit B proposal.
- P. 23 creation services, p. 44 HPLHS and p. 49 resources: verify edition and selected asset access/license when used. No third-party downloads are bundled by this guide.

Missing evidence produces an exact pending question, no speculative charge and an independent next action. It does not block supported preparation/narration.

## X - Suggestions not adopted as requirements

Personal enthusiasm, particular films/music, purchases, convention attendance and external playtesting are optional inspirations. Always saying yes, denying prior narration, predetermining helplessness, disabling every technology or secretly imposing an ending conflict with reliable adjudication; use R, T and D instead. Repeated tips share maintained procedures. No full book, translation, illustration or private source path is distributed.

## Persist and resume

Use [the existing ledger](session-runtime.md). Read `view --gm`, copy the entire `private` object, update `private.keeper` and relevant `private.review` fields, then submit one sourced `private` change with current revision/profile and a new ID. Replacement semantics require preserving unrelated timers, dice settings and plans. Preserve existing pending tasks. Observations use separate audience-labelled facts in the same event.

`keeper` is an optional notes convention, not a newly validated schema or automatic scheduler. Do not duplicate HP/SAN totals. If Dice local owns resources, the narrative ledger must not hold independently writable copies; reference applied operations. Cross-database changes are not atomic: reconcile partial failure before continuing dependent work.

Cold-read GM state and separate player views after saving. Resume from last operation, pending intent, group times, next actor, released handouts and rulings. Do not reroll, disclose or charge on replay. The supplied cases are synthetic walkthroughs, not live-player evaluation.
