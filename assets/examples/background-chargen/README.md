# Background creation acceptance cases

Three original settings, two proposed characters each. All use explicitly approved **fixture-only CoC 7 house profiles** to isolate changes caused by setting and activities. They are not official Dark Ages, Down Darker Trails or Doors to Darkness builds. No player has approved these fictional identities for a real campaign. These profiles do not replace other systems' creation rules.

| Case | Public specification and complete cards | GM research/adaptation | Machine input |
|---|---|---|---|
| c.1000 southern English monastery; archive/rural investigation | [Player](monastery/player.md) | [GM](monastery/gm.md) | [JSON](monastery/spec.json) |
| 1884 Colorado railway town; freight/field pursuit | [Player](railway/player.md) | [GM](railway/gm.md) | [JSON](railway/spec.json) |
| 1925 New York harbor; documentary/social investigation | [Player](harbor/player.md) | [GM](harbor/gm.md) | [JSON](harbor/spec.json) |

Run `python -X utf 8 scripts/background_chargen.py assets/examples/background-chargen/monastery/spec.json`; add `--player` for a whitelisted card export. Repeat for railway and harbor. Each `cards.json` is the checked player projection; each `player.md` includes the complete skill table, not only invested skills. `spec.json` contains a synthetic GM secret used in leakage tests, so do not hand that file to players.

Six controlled attribute sets use the same fixed numbers, explicitly declared as test inputs, so role/setting comparisons do not confuse better attributes with better rules. All characters are age 28; the supplied EDU improvement result 60 does not improve EDU 70. The guide uses EDU×2+STR×2=240 occupation points; the other profiles use EDU×4=280 or EDU×2+DEX×2=280. Everyone spends INT×2=150 interest points. Different budgets preserve the declared formula rather than forcing equal final percentages.

The cap 80 and zero starting Mythos are fixture choices. Skill bases come from the core except the recorded monastery changes. Ordinary unlisted specialties use the system's applicable specialty rule after being added to the profile; the tool refuses unknown IDs instead of assigning an invented base. No historic price research was completed: existing goods and grants are explicitly prescribed, not claimed to reproduce a medieval or 1884 market. New purchases would reopen that research question.

## Rejected/error cases

Automated tests reject over-budget allocation, changed row base, wrong edition, unknown specialty, ineligible occupation points, prohibited interest spending, over-cap skills, unlisted equipment, inconsistent money and duplicate IDs. Missing evidence and unapproved house rules return draft status. The output whitelist omits synthetic GM notes and hidden routes; text already put into a public card field still needs human/GM audience review.

This is complete creation under the declared fixture profiles plus source and arithmetic review. The historical veracity of fictional allowances is not asserted. Other ages, high Build, alternate generation methods and other systems must use their own complete procedures rather than silently extending this narrow adapter.
