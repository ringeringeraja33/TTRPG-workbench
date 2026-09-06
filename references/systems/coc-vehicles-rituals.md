# CoC7 vehicle and ritual operations

Use the local Chinese core v1.2.1, PDF page numbers below. Keep its SHA-256 and translation identity with the campaign. Official [Magic rules](https://callofcthulhuwiki.chaosium.com/rules/magic.html) corroborate first-cast checks, failed pushes and MP overflow. Never transfer a table from CoC6 or a supplement without an explicit profile choice.

## Vehicle state and chase sequence

Source: core PDF122–129. Track original/current Build, MOV and adjusted MOV, driver and passengers, DEX order, AP budget/debt, location, impaired handling, vehicle type and source. The vehicle reference table's MOV values describe modern vehicles; consult its period adjustment for a 1920s campaign instead of silently retaining modern values.

For each driver action: declare movement/acceleration and AP, describe the approaching hazard, establish skill/difficulty and modifiers, roll, resolve progress and any delay, then collision damage if appropriate. A failed hazard does not automatically mean a collision of the worst category. Distinguish a hazard roll from paying to clear a barrier. Passengers act separately with their own actions; an assistance roll does not give each passenger the driver's AP. Preserve delay beyond the present round as AP debt. Branch the location graph for split routes.

## Collision settlement

Core PDF126–127 defines occupants and delay; PDF129 gives severity. Normal/hard/extreme hazards suggest minor/moderate/serious accidents when the fictional circumstances do not specify something else. The table's damage expressions are respectively `1d3-1`, `1d6`, `1d10`, `2d10`, `5d10` for its five severity bands. The last two represent much greater impacts, not extra difficulty categories.

Roll vehicle damage in **Build** units. Separately roll the same severity expression as **HP** damage for each occupant. Do not copy the driver's roll to everyone. Passenger armor in the vehicle table protects against external attacks; it does not subtract from this collision injury. Most collisions also cause a separately determined `1d3` AP delay; omit or change this only through an explicit situational ruling. `collision` calculates the common delayed-collision case from supplied outcomes; it does not roll dice or choose severity.

Ordinary attack damage converts at ten damage per Build, dropping the remainder of that hit and ignoring hits below ten. Collision damage already expressed in Build must never be divided by ten. At current Build no greater than half the original Build, rounded down, handling suffers one penalty die. Build0 is inoperable. A single collision dealing at least the original Build is catastrophic; incremental wear reaching0 is a different situation. Survival, secondary crashes and ejection need the source's situational ruling. `vehicle_damage` flags these branches rather than automatically killing every occupant. It currently accepts integer Build vehicles; fractional-Build entries such as bicycles require direct source adjudication.

Worked fixture: original Build5, current5, moderate accident; vehicle roll3, driver HP roll1, passenger HP roll6, delay2. Save Build2 and the handling penalty, distinct HP losses and two delayed AP. Run ordinary injury checks separately for each occupant. Later losing the last two Build incrementally does not retroactively turn this into a single-hit catastrophic accident.

## Learning, first casting and interruption

Core PDF155–157: studying a spell from a tome requires prior initial reading; default study is typically 2d6 weeks with Hard INT, subject to the stated Keeper timing. A teacher typically reduces study to 1d8 days. Failed study, a pushed study roll, relearning, and first casting are distinct states. Record the learning source, time spent and result. Learning a spell is not permission to invent its costs or effects.

The first casting normally requires Hard POW; NPCs/monsters and established spells do not use this routine first-cast roll. A failed first attempt has no effect and costs the attempt. A later second attempt is a push unless the character takes the source's relearning route. Pay a fresh set of costs for the pushed attempt. A failed push still produces the spell and also causes dire consequences. The core's backlash adds 1d6 multiples of spell costs on top of costs already paid; roll the corresponding SAN dice as required rather than multiplying a previous lucky SAN result. Resolve permanent POW separately from regenerating MP.

`casting_outcome` separates whether the effect occurs from whether costs are paid. `magic_payment` spends MP then applies remaining MP loss one-for-one to HP. Feed that HP injury into the existing injury/major-wound procedure. This helper does not spend SAN or POW for you and does not establish material or ritual eligibility.

Worked backlash fixture, core PDF156: after paying two 4MP attempts from13MP, 5MP remains. An additional16MP backlash spends those5 and inflicts11HP damage; an initially uninjured13HP caster has2HP and needs the applicable major-wound check. The spell has still taken effect. Apply the separately rolled SAN loss and any manifestation consequences before handing control back.

An interrupted casting fails while retaining its MP and SAN cost; record the interruption and any Keeper-determined additional consequence. This is not D&D's concentration-save procedure. Instantaneous spells activate at DEX+50; one-round spells at current-round DEX; a two-round spell at next-round DEX, per official Magic guidance. Keep both casting progress and end time.

## Turning an actual ritual entry into an executable card

The core's spell chapter begins at PDF214. Use `scripts/library.py read <book> --query <spell-name> --start 214 --limit 8 --chars 5000`, then read continuation pages. Search aliases only to locate the canonical entry; similar names can designate different variants.

Record the exact variant, learning source, known/successfully-cast state, caster and consenting contributors, location/time/astronomical conditions, materials and consumptions, MP/SAN/POW costs, casting duration, target, resistance/binding procedure, outcome, interruption and backlash. Check each contribution permission in the particular spell. Summoning does not imply binding, control or harmless arrival. Give a summoned being its own immediate behavior and observation/SAN consequences where required.

Examples to load rather than replacing with a generic ritual:

- **Elder Sign / 旧印开光术**, core PDF227 onward: permanent10POW, one-hour casting. Continue to its actual protection and placement text; spending10MP is incorrect.
- **Shrivelling / 枯萎术**, PDF235: declared MP investment, associated SAN cost, instantaneous timing and opposed POW. Separate first-cast success from the spell's target opposition. The deeper variant is a separate rules card.
- **Golden Mead / 黄金蜂蜜酒酿造术**, PDF219 onward: brewing and activating/using the drink have different costs and timing, with a travel-distance table. Do not treat paying the brewing MP as also paying the journey cost.

Save resource costs, injury flags, ritual progress and source-backed facts in one ledger event. Keep undiscovered effects in GM private state, while showing players what their characters can observe. Programmatic cases and source review are the acceptance criteria; live-player evaluation is excluded from this work.
