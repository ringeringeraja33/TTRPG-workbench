# Advanced mechanics: verified boundaries

Read the selected system procedure first. Helpers in `scripts/rules_extended.py` accept declared inputs and return proposed outcomes. They neither roll dice nor spend campaign resources. Commit the adjudicated result once through the session ledger. These helpers are deliberately narrower than a complete combat engine.

## Call of Cthulhu 7: automatic fire and vehicles

Source: local Chinese Keeper Rulebook v1.2.1, PDF pages 97–100 and 122–125 (PDF page numbering, not printed pages). Consult the actual weapon entry. Automatic fire, burst fire, multiple handgun shots and slow single-shot weapons use different procedures.

For full automatic fire, declare ammunition and volleys before rolling. A volley can contain up to one tenth of the skill, rounded down, with a minimum of three. Smaller declared volleys are allowed within that range. At skill 63, three volleys of four use twelve rounds. Reserve ammunition wasted when shifting between targets as well. Each volley requires its own roll; subtract ammunition even on a miss. Apply armor separately to each bullet that hits.

`coc_volley_plan(63, [4,4,4], 15, waste=2)` reserves fourteen rounds. With normal initial difficulty and no other modifiers, volley penalties are zero, one, then two dice; subsequent volleys retain two penalty dice and increase difficulty. The helper does not combine situational bonus/penalty dice, handle restricted firing arcs, or decide whether a target change is possible. Supply those adjudications separately. Ordinary successful volleys hit with half their bullets, rounded down with at least one. An extreme result normally hits with all bullets, half of them impaling; if extreme success was required to hit, it gives the ordinary hit result. Critical-only shots and fumbles are intentionally rejected by `coc_volley_hits` pending full adjudication.

Vehicle chase checklist: record adjusted MOV, driver, passenger positions, AP and carried delay. If using acceleration, declare distance and AP before the hazard: two or three locations for an AP incur one penalty die; four or five incur two. Failure stops progress; a later attempt pays anew. Do not automatically apply the acceleration penalty to barriers. A passenger has one action in DEX order and can assist navigation/observation; they do not gain the driver's chase AP. Moving-vehicle shooting has its own penalty. Driver injury, vehicle build damage and occupant injuries are separate checks. The expanded [vehicle and ritual package](coc-vehicles-rituals.md) supplies the collision procedure and numerical helpers.

Acceptance: insufficient ammunition including target-transition waste must reject before any roll; odd volleys must round down; extreme-range fire must not acquire ordinary-range impaling benefits; a collision must use verified severity and separately supplied vehicle and occupant rolls.

## D&D SRD 5.2.1: slot expenditure is per turn

Source: SRD 5.2.1 PDF page 105, “One Spell with a Spell Slot per Turn”; official distribution through [D&D SRD](https://www.dndbeyond.com/srd). Record an actor-specific turn identity such as `round3.goblin2`, not only a round number.

`dnd_slot_cast` checks only the limit on expending slots to cast spells. A slotted spell on your turn and a slotted reaction on an enemy's turn do not share that limit. A slotted reaction during your own turn does. Casting without a slot does not consume this allowance, but still requires its own action, components, legal target and any feature-specific restrictions. Action Surge does not authorize a Magic action under this edition. Do not import the 2014 bonus-action spell restriction into this profile.

Store the updated list in private rules state in the same event that spends the slot and reaction/action. Replaying an event must not reserve or spend a second time. Changing editions is a migration decision, never an implicit conversion. This helper does not validate spell preparation, multiclass slot tables, components, Counterspell, or feature exceptions.

## Fate Condensed: absorb, concede, recover

Sources: [conflicts and recovery](https://fate-srd.com/fate-condensed/challenges-conflicts-and-contests), [advancement](https://fate-srd.com/fate-condensed/advancement). Standard stress boxes absorb one shift each; consequences absorb two, four or six. `fate_absorb` takes only currently available slots and boxes. It reports taken out if the chosen capacity cannot absorb the entire hit; it does not choose consequences for the player. Session state must mark used boxes and slots so they cannot be reused.

Concession must precede the opposing roll. Negotiate losing terms, leave the conflict, and record the Fate-point award due at its end: one plus the number of consequences received in this conflict. Concession does not erase consequences. Stress clears at scene end. Recovery requires treatment, a renamed recovering aspect and the appropriate interval; self-treatment raises difficulty by two. A moderate consequence treated in the last scene needs a full subsequent session, not merely crossing a session boundary.

At a milestone use Condensed's lateral changes; do not substitute Core's milestone tiers. At a breakthrough consult its explicit advancement and recovery options, preserve the skill-column constraint, and record each selected change. See the existing [Fate procedure](fate-blades-procedures.md) for the remaining core workflow.

## Blades in the Dark: vice and downtime

Sources: [vice](https://bladesinthedark.com/vice), [downtime](https://bladesinthedark.com/downtime-activities), [trauma](https://bladesinthedark.com/stress-trauma), [official player kit](https://evilhat.com/wp-content/uploads/2022/05/blades_playerkit_v8_2.pdf), creation on PDF page 2. Lock the original rules or an explicit supplement profile before play.

`blades_vice` receives the already-resolved vice die result. Clearing exactly the marked stress is safe; clearing more causes overindulgence. Use the lowest attribute to establish the pool and the system's zero-dice procedure where needed. Two free downtime activities become one at war; every additional activity costs one coin or rep. Ordinary conversations and information gathering do not automatically consume these activity slots. `blades_downtime_cost` computes only the extra activity cost, excluding coin spent to improve a roll.

Trauma removes the character from the current action. On return stress is cleared and vice is satisfied for the next downtime; this is not an extra free activity or automatic harm recovery. Record a fourth trauma as retirement. For creation add four action dots to the selected playbook's starting dots, with no action above two; record heritage, background, ability, friend, rival, vice/purveyor and appearance. Derive attributes from the first column, not the sum of all action dots. Load is selected before a score; specific equipment is marked when introduced, respecting its load cost. Crew creation and playbook-specific exceptions still require the corresponding source.
