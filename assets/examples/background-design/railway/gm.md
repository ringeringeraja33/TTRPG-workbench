# Two Times on One Receipt — GM dossier

Reuse [the original creation research and occupation comparison](../../background-chargen/railway/gm.md). This pack adds original materials and scene design, not a reproduction of that comparator module.

History source: [https://blogs.loc.gov/law/2024/11/whose-time-is-it-anyway-a-brief-history-of-standardized-time-zones-in-the-united-states/](https://blogs.loc.gov/law/2024/11/whose-time-is-it-anyway-a-brief-history-of-standardized-time-zones-in-the-united-states/). Prior background-chargen review read the 1883 standard-time and telegraph discussion. On 2026-09-06 current search returned relevant excerpts, direct article access returned 403; alternative LOC guide returned 429. Current pack does not claim fresh full-text access. The town, wiring, local clock disagreement and access permissions are original assumptions; no exact offset or price is inferred.

## Rule and inference ledger

History establishes the broad context only. Local people, buildings, disputes, access permissions, loans, consumable limits and delay clocks are original scenario decisions. No new creation points, skill bases, weapon statistics or automatic dice modifiers are added. With no sourced price list, use explicit allocations; a request to purchase or own new equipment reopens the budget and availability review.


## Connected scenes

### office: Station office

Separate time notation from the cargo allegation. Two clocks disagree with a handwritten receipt. Reach it through the preceding lead; the first scene is the agreed starting appointment.

NPC: Clerk Mara wants the station cleared of theft accusations; she will explain log conventions but not release every message.

Objects: Message copy, wall clock, freight destination list.

GM clue: The notation discrepancy points to the loading siding; it does not prove a theft.

Pressure: Original shared delay counter starts at 0. Each failed specialist attempt or ordinary route adds 1; at the first total of 3 the primary NPC leaves. The named ordinary-route contact stays available. Further delays do not remove that contact. No automatic HP/SAN loss.

- office-technical: Ask how the apparatus and log were used, then inspect a permitted connection. Skills: ['Electrical Repair']; items: ['message-copy']. One investigative attempt; on failure add one delay and use a different route or meet native-system retry conditions. Success: The notation discrepancy points to the loading siding; it does not prove a theft. Failure: A failed inspection delays confirmation; Mara names the siding but cannot vouch for the disputed timestamp. Success -> siding; failure -> office.

- office-social: Negotiate the specific cooperation described in the NPC entry. Skills: ['Persuade']; items: []. An interview and an offered favor; decline or failed persuasion leaves the ordinary route available. Success gains a more precise account with permission; failure withholds that cooperation, not every onward lead. Success -> siding; failure -> office.

- office-ordinary: Platform porter Ames orally reads the loading destination from the public freight notice: the siding. Ames remains on shift after Mara leaves; the disputed timestamp is not confirmed. Skills: []; items: []. One delay; no special equipment or successful skill roll. Accept less precise evidence and the stated access limits. After a failed specialized attempt, take this separate limited lead and pay the ordinary delay. Platform porter Ames orally reads the loading destination from the public freight notice: the siding. Ames remains on shift after Mara leaves; the disputed timestamp is not confirmed. Success -> siding; failure -> siding.

Exit: Follow the next lead or leave with an explicitly incomplete report at the final scene.

### siding: Loading siding

Determine which route the wagon took. Crate splinters lie beside a public footpath. Reach it through the preceding lead; the first scene is the agreed starting appointment.

NPC: Inspector Cole wants the line safe; he trades a guided look for an accurate damage report.

Objects: Route sketch, wagon impressions, broken packing strip.

GM clue: A wagon proceeded to the inland storehouse, not the outbound platform.

Pressure: Original shared delay counter starts at 0. Each failed specialist attempt or ordinary route adds 1; at the first total of 3 the primary NPC leaves. The named ordinary-route contact stays available. Further delays do not remove that contact. No automatic HP/SAN loss.

- siding-technical: Compare fresh impressions along the permitted path. Skills: ['Track']; items: ['route-sketch']. One investigative attempt; on failure add one delay and use a different route or meet native-system retry conditions. Success: A wagon proceeded to the inland storehouse, not the outbound platform. Failure: Wind obscures the marks; Cole offers a slower guided route without confirming the exact wagon. Success -> store; failure -> siding.

- siding-social: Negotiate the specific cooperation described in the NPC entry. Skills: ['Persuade']; items: []. An interview and an offered favor; decline or failed persuasion leaves the ordinary route available. Success gains a more precise account with permission; failure withholds that cooperation, not every onward lead. Success -> store; failure -> siding.

- siding-ordinary: Crossing attendant Beck describes the public path to the inland storehouse. Beck remains posted when Cole leaves; the route gives access without confirming which wagon made the tracks. Skills: []; items: []. One delay; no special equipment or successful skill roll. Accept less precise evidence and the stated access limits. After a failed specialized attempt, take this separate limited lead and pay the ordinary delay. Crossing attendant Beck describes the public path to the inland storehouse. Beck remains posted when Cole leaves; the route gives access without confirming which wagon made the tracks. Success -> store; failure -> store.

Exit: Follow the next lead or leave with an explicitly incomplete report at the final scene.

### store: Inland storehouse

Reconstruct the failed transfer. A strained latch catches on an uneven door. Reach it through the preceding lead; the first scene is the agreed starting appointment.

NPC: Storekeeper Venn fears a negligence claim; he permits a witnessed inspection and can offer an oral account.

Objects: Latch, packing list, signed arrival stub.

GM clue: The cargo remained inland during an unrecorded repair; responsibility depends on whose instructions were followed.

Pressure: Original shared delay counter starts at 0. Each failed specialist attempt or ordinary route adds 1; at the first total of 3 the primary NPC leaves. The named ordinary-route contact stays available. Further delays do not remove that contact. No automatic HP/SAN loss.

- store-technical: Inspect the idle latch with a mechanic and compare the arrival stub. Skills: ['Mechanical Repair']; items: ['repair-kit']. One investigative attempt; on failure add one delay and use a different route or meet native-system retry conditions. Success: The cargo remained inland during an unrecorded repair; responsibility depends on whose instructions were followed. Failure: Failure leaves the mechanical cause unresolved; the witnessed oral account still establishes where the cargo waited. Success -> END; failure -> store.

- store-social: Negotiate the specific cooperation described in the NPC entry. Skills: ['Persuade']; items: []. An interview and an offered favor; decline or failed persuasion leaves the ordinary route available. Success gains a more precise account with permission; failure withholds that cooperation, not every onward lead. Success -> END; failure -> store.

- store-ordinary: Relief worker Dale gives the public arrival time from the shift handover. Dale stays after Venn leaves; the party can report that cargo waited here while the mechanical cause remains unresolved. Skills: []; items: []. One delay; no special equipment or successful skill roll. Accept less precise evidence and the stated access limits. After a failed specialized attempt, take this separate limited lead and pay the ordinary delay. Relief worker Dale gives the public arrival time from the shift handover. Dale stays after Venn leaves; the party can report that cargo waited here while the mechanical cause remains unresolved. Success -> END; failure -> END.

Exit: Follow the next lead or leave with an explicitly incomplete report at the final scene.

## Expansion directions

- Procedural mystery: compare time notation and custody; no numerical time-offset puzzle without researched local standards.

- Frontier suspense: a departing witness creates pressure; arrange transport as a sourced service or explicit allowance, not free horse ownership.

- Industrial ghost story: let a repeated message suggest a lost worker; adding dangerous machinery or supernatural combat requires separate sourced procedures.

## Acceptance walkthrough

Two original builds reuse `railway/spec.json`: Telegrapher 280/280 occupation, 150 interest, Track inspector 280/280 occupation, 150 interest.

With no optional items or successful specialist checks, follow: office -> siding -> store -> END. Each transition uses the stated ordinary opportunity, pays delay and preserves only the limited evidence. At three delays move the cooperative witness off-site and use their designated public/custodian channel; never delete the onward route. This is a structural and prose walkthrough, not live play.

The player projection omits all scenes, clue destinations and the synthetic GM marker. Public item descriptions were reviewed separately. The tool checks registered fields; it cannot infer whether an item is historically available or whether text placed in a public field reveals an answer.



No-item walkthrough: ordinary scene 1 adds delay 1, ordinary scene 2 adds delay 2, ordinary scene 3 adds delay 3 and fires primary-NPC departure once. The named ordinary contacts persist, so the final report remains possible with the documented uncertainties.

Prior-failure walkthrough: a failed technical attempt adds delay 1 and retains the current scene; its ordinary alternative adds delay 2 and reaches scene 2. The next ordinary route reaches delay 3 and moves primary NPCs away. Scene 3 uses its named alternate contact, adds delay 4 and reaches END. This records access and information loss rather than converting failed technical work into success.

Equipment boundary: a lost message copy, unreadable sketch or missing repair-kit part makes that item route unavailable. Use the named contact instead; an item is not restored merely by changing scenes. The tool tests the stronger no-item case, not physical wear or automatic inventory tracking.
