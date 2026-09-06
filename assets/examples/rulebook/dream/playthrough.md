# Twenty-turn narrative companion — GM only

These are original simulated decisions using the rules and declared dice in `rulebook_demo.py`. Read [the scenario](scenario.md) separately from the player files. The generated trace records numeric pre/post state; this companion records what the same actions mean in the fiction. No player behavior was observed.

| Turn | Declared intent and input | Consequence and next option |
|---|---|---|
| 1 | Iona compares salt stains, Trace 2, die 1 | Partial index, progress 1, strain 1; a ferry seal can be examined |
| 2 | Sen spends greenhouse memory B-0 to help Iona read the damp shelf | B-0 fades, Iona has help 1; no progress from help alone |
| 3 | Iona spends A-0 and compares tide dates, Trace 2, die 2, help 1 | Total 6, progress reaches 3; both bonus sources consumed |
| 4 | Sen rebinds the salt index, Weave 2, die 6 | Total 8, progress reaches 5; complete truth recoverable at deadline |
| 5 | Iona grounds herself using thread, recover | Strain 1 to 0; scene ends with complete ferry archive, next cabin opens |
| 6 | Sen questions a conductor, Listen 0, die 1 | Failed contact, strain 2; a damaged dock sign indicates the bell room, motive unknown |
| 7 | Iona offers fresh A-1 for Sen's fresh B-1 with consent | Ownership changes, both remain fresh; no time-free duplicate exchange |
| 8 | Sen spends borrowed A-1 to repair the ferry, Weave 2, die 2 | Progress 2; Iona's tide memory is now faded in Sen's custody |
| 9 | Iona spends borrowed B-1 and compares tickets, Trace 2, die 1 | Total 4, progress 3, strain 1; motive still uncertain |
| 10 | Sen steadies himself, recover | Strain 2 to 0; damaged archive but bell-room route remains; save and reload here |
| 11 | Iona listens for a keeper, Listen 1, die 1 | Total 2, strain 3; a broken nameplate is a fragment, not proof of authorship |
| 12 | Sen transcribes an interval, Trace 1, die 1 | Total 2, strain 2; marks conflict, other methods remain available |
| 13 | Iona repeats a changed question, Listen 1, die 1 | New action pays its own time; strain 5, no free retry |
| 14 | Sen compares another interval, Trace 1, die 1 | Strain 4; cabinet direction is known despite no complete archive |
| 15 | Iona calls into the fading note, Listen 1, die 1 | Strain caps at 6, fractured; damaged bell archive leads to cabinet |
| 16 | Iona grounds herself at the cabinet, recover | Strain 6 to 4; she can delve again, one recovery used this scene |
| 17 | Sen takes his recovery turn | Strain 4 to 2; no memory becomes fresh |
| 18 | Iona cross-references shores, Trace 2, die 4 | Progress 2; two possible histories are visible |
| 19 | Sen spends B-2 to join compartments, Weave 2, die 3 | Progress 4; return promise fades |
| 20 | Iona spends A-2 to align dates, Trace 2, die 2 | Progress 6 caps at 5; complete cabinet archive, expedition ends |

Two complete archives yield a contested reconstruction. The ferry's motive and keeper's authorship remain unknown. Iona raises Listen from 1 to 2; Sen raises Trace from 1 to 2. Their remaining strain is 4 and 2; all six memories are faded. No growth refund occurs. Players would choose their own emotional responses to these losses.

## Analysis and remaining design questions

Exact one-action enumeration with no help: skill 0, spend 0 has full/partial/failure each 1/3; skill 2, spend 0 has full 2/3 and partial 1/3; skill 2, spend 2 guarantees a full result under this model. This makes a two-card burst useful under a deadline, while consuming two of only six shared fresh memories. It does not prove expedition strategy is balanced.

A weakly motivated action surfaced: with a capable helper and no fictional access restriction, two independent unboosted skill-2 delves yield uncapped expected progress 10/3. Help followed by one skill-2 delve gives only 11/6 and consumes a memory. This comparison ignores scene caps, fracture, different access and future ownership; it is a diagnostic of the current help cost, not a dominance proof for every state. Retain it as an explicit open design issue for the next prototype, rather than quietly changing a rule mid-replay. One candidate revision would allow help within an existing action and adjust its benefit; it requires new costs and fresh tests before adoption.

The repeated low dice in scene three are adversarial fixtures, not a sampled estimate of fracture frequency. The tests show recovery and onward routes remain executable. No claims about fun, optimal play, long campaigns or live-player validation follow.
