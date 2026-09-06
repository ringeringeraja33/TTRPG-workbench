# Lantern Couriers — organizing scattered notes

Synthetic source notes, invented for this acceptance case:

- N1: "No dice. Couriers deliver promises across islands. Call the payment ember."
- N2: "A bag holds three packets. The short route costs two fuel; the long route costs one and arrives late."
- N3: "Once per trip, trade a personal favor for one ember. Players can reject a delivery."

## Retained intent and additions

| Note | Destination | Editorial action / new design |
|---|---|---|
| N1 | Premise and glossary | Retain diceless travel and ember; replace N2's fuel alias only |
| N2 | Creation and travel | Retain capacity and both route costs; add explicit timing and consequences |
| N3 | Bargains and ending | Retain refusal and once-per-trip favor; add an enforceable used flag and pending obligation |

Provisional additions: starting ember 2, cap 3; two players; a trip includes one delivery route; late delivery earns no ember; timely delivery earns 1. These numbers are original fixture decisions, not an inferred official system. No combat, spell, injury or random encounter subsystem is needed for this delivery-focused minimum. Player agreement resolves conflicting plans; if disagreement persists, each can refuse without cost and the trip ends. No character is forced to accept a favor or belief.

## Playable chapter and glossary — version 0.1

A packet is one promise written by a named sender for a named recipient. Each courier names themselves, a motive, a connection to the other courier and one person who may request a favor. Each starts with a bag (capacity three packets), two ember (integer range 0–3) and an unused favor flag. There are no attributes or random checks. Packets and ember are separate; all transfers require both players' consent, preserve totals and respect destination capacity. Overflow transfers fail without changing either inventory.

At the depot, choose up to three offered packets per courier; accepting each occupies one bag slot. There is no fee and a player may refuse any packet. Announce the destination, deadline and late consequence before accepting. Once per trip at the depot, a courier may accept a named obligation to a named person to gain one ember, only if below cap. Set favor-used immediately. No refund and no repeated use by renaming the favor; settling the obligation does not reset the flag that trip.

Choose a route together: short costs each traveling courier two ember and arrives before the deadline; long costs each one and arrives late. Pay before departing. Insufficient ember makes that route unavailable, with no payment by anyone until all travelers can afford it. Traveling couriers may transfer ember at the depot, but may not borrow below zero. A courier may stay behind, return accepted packets and end their trip with no reward or cost. No free retry changes a late delivery to timely.

At arrival, remove each delivered packet from its carrier's bag. A timely delivery of at least one accepted packet grants its carrier one ember total for the trip, irrespective of packet count; cap at three and discard overflow. A late delivery grants zero and the recipient names one damaged relationship; players decide their own responses. Return travel is abstracted and costs nothing; it grants no delivery or favor reward. This closes the trip. For the next trip clear favor-used and offer new contracts; ember and unresolved obligations persist. Growth is fictional access: after settling an obligation, the GM may offer a new contact, with no automatic numeric reward. Repeated timely routes cost 2 and earn 1, so repeating deliveries alone loses one ember per courier.

## Complete characters and route test

Mira: wants to deliver her teacher's last promise; knows Sol from ferry work; owes no favor yet; contact Eda; bag with packets P1 and P2, ember 2/3, favor unused. Sol: wants to repair trust with a recipient; trusts Mira's navigation; contact Ren; bag P3, ember 2/3, favor unused. Both own bags and no other mechanical gear or abilities.

Short route: each pays 2, both reach ember 0; delivery empties both bags and each earns 1, ending at ember 1. Two packets do not give Mira two rewards. Alternative long route: each pays 1, ending at ember 1; both arrive late, no reward, bags emptied and recipient records the damaged relationship. Identical ember endpoints have different fictional effects. The short route is better for this isolated initial state; across repeated trips it can become unaffordable. This prototype has no claim of equal strategic value for both choices.

Boundary: Mira at ember 3 cannot accept another favor for a nonexistent gain. A transfer of one ember to her fails without spending Sol's ember. Empty bags cannot earn a delivery reward. Correction applied after editorial review: reward now explicitly requires at least one accepted packet actually delivered; route arrival alone cannot generate income. The canonical arrival paragraph now includes this eligibility rule.

## Maintenance and acceptance record

Canonical terms: ember (currency), packet (promise and bag slot), trip (depot through delivery/return), obligation (persistent fiction), favor-used (once-per-trip gate). The route table, character record and reward example must change together if route costs change. Research comparison uses [the shared source ledger](../../../references/rulebook-sources.md); no published dice mechanic was imported. The two route calculations and cap/refusal/empty-delivery checks are paper examples, not a twenty-turn engine or long-campaign balance test. Next decision: whether obligations should become a formal long-term subsystem.
