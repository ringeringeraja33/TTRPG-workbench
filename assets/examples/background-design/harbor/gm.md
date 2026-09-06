# A Receipt without a Landing — GM dossier

Reuse [the original creation research and occupation comparison](../../background-chargen/harbor/gm.md). This pack adds original materials and scene design, not a reproduction of that comparator module.

History source: [https://www.archives.gov/publications/prologue/2011/fall/smugglers-bootleggers-scofflaws](https://www.archives.gov/publications/prologue/2011/fall/smugglers-bootleggers-scofflaws). Opened 2026-09-06: Ellen NicKenzie Lawson, Prologue Fall 2011, maritime smuggling and Coast Guard records. Supports coastal/documentary context. Article late-1920s technology does not establish 1925 personal radio access. No historical individual, legal permission or market price is imported.

## Rule and inference ledger

History establishes the broad context only. Local people, buildings, disputes, access permissions, loans, consumable limits and delay clocks are original scenario decisions. No new creation points, skill bases, weapon statistics or automatic dice modifiers are added. With no sourced price list, use explicit allocations; a request to purchase or own new equipment reopens the budget and availability review.


## Connected scenes

### ledger: Freight office

Identify which quantity is disputed. A damp ledger carries two different totals. Reach it through the preceding lead; the first scene is the agreed starting appointment.

NPC: Clerk Neri wants the worker treated fairly but fears losing employment; she shares a selected entry.

Objects: Ledger copy, delivery list, blotter.

GM clue: The discrepancy belongs to a quayside transfer, not the entire ship's cargo.

Pressure: Original shared delay counter starts at 0. Each failed specialist attempt or ordinary route adds 1; at the first total of 3 the primary NPC leaves. The named ordinary-route contact stays available. Further delays do not remove that contact. No automatic HP/SAN loss.

- ledger-technical: Compare the two entries and their recorded units. Skills: ['Accounting']; items: ['ledger-copy']. One investigative attempt; on failure add one delay and use a different route or meet native-system retry conditions. Success: The discrepancy belongs to a quayside transfer, not the entire ship's cargo. Failure: Failure leaves the amount uncertain; Neri identifies the relevant quay and the limit of her knowledge. Success -> quay; failure -> ledger.

- ledger-social: Negotiate the specific cooperation described in the NPC entry. Skills: ['Persuade']; items: []. An interview and an offered favor; decline or failed persuasion leaves the ordinary route available. Success gains a more precise account with permission; failure withholds that cooperation, not every onward lead. Success -> quay; failure -> ledger.

- ledger-ordinary: Dispatch runner Jo orally repeats the selected quay from the public delivery board. Jo remains assigned after Neri leaves; the exact disputed quantity remains unconfirmed. Skills: []; items: []. One delay; no special equipment or successful skill roll. Accept less precise evidence and the stated access limits. After a failed specialized attempt, take this separate limited lead and pay the ordinary delay. Dispatch runner Jo orally repeats the selected quay from the public delivery board. Jo remains assigned after Neri leaves; the exact disputed quantity remains unconfirmed. Success -> quay; failure -> quay.

Exit: Follow the next lead or leave with an explicitly incomplete report at the final scene.

### quay: Public quay

Find who observed the transfer. An exposed crate label flaps behind a railing. Reach it through the preceding lead; the first scene is the agreed starting appointment.

NPC: Porter Ellis wants no trespass; he offers a public view and names a witness in return for accurate attribution.

Objects: Visible label, request card, porter's shift note.

GM clue: A receipt was carried to a nearby lodging house before the cargo complaint.

Pressure: Original shared delay counter starts at 0. Each failed specialist attempt or ordinary route adds 1; at the first total of 3 the primary NPC leaves. The named ordinary-route contact stays available. Further delays do not remove that contact. No automatic HP/SAN loss.

- quay-technical: Inspect the permitted crate exterior and visible label. Skills: ['Spot Hidden']; items: ['inspection-card']. One investigative attempt; on failure add one delay and use a different route or meet native-system retry conditions. Success: A receipt was carried to a nearby lodging house before the cargo complaint. Failure: Failure or refused access prevents close inspection; Ellis supplies a slower witness route without confirming the hidden crate contents. Success -> lodging; failure -> quay.

- quay-social: Negotiate the specific cooperation described in the NPC entry. Skills: ['Persuade']; items: []. An interview and an offered favor; decline or failed persuasion leaves the ordinary route available. Success gains a more precise account with permission; failure withholds that cooperation, not every onward lead. Success -> lodging; failure -> quay.

- quay-ordinary: Public porter Pat names the nearby lodging-house witness from a delivery recollection. Pat remains after Ellis leaves; no crate contents or private cargo access is granted. Skills: []; items: []. One delay; no special equipment or successful skill roll. Accept less precise evidence and the stated access limits. After a failed specialized attempt, take this separate limited lead and pay the ordinary delay. Public porter Pat names the nearby lodging-house witness from a delivery recollection. Pat remains after Ellis leaves; no crate contents or private cargo access is granted. Success -> lodging; failure -> lodging.

Exit: Follow the next lead or leave with an explicitly incomplete report at the final scene.

### lodging: Lodging-house interview

Choose what to report and how to protect a source. A tired witness asks that names stay off the public notice. Reach it through the preceding lead; the first scene is the agreed starting appointment.

NPC: Witness Ro fears retaliation; they agree to describe the handover if identity stays private.

Objects: Receipt notebook, voluntary account, returned stub.

GM clue: The handover account contradicts the accusation but leaves the final cargo recipient unresolved.

Pressure: Original shared delay counter starts at 0. Each failed specialist attempt or ordinary route adds 1; at the first total of 3 the primary NPC leaves. The named ordinary-route contact stays available. Further delays do not remove that contact. No automatic HP/SAN loss.

- lodging-technical: Clarify what the existing receipt claims, then record a voluntary statement. Skills: ['Law']; items: ['receipt-book']. One investigative attempt; on failure add one delay and use a different route or meet native-system retry conditions. Success: The handover account contradicts the accusation but leaves the final cargo recipient unresolved. Failure: Failure leaves the receipt's implications unresolved; a witnessed oral account can still correct the chronology without a legal conclusion. Success -> END; failure -> lodging.

- lodging-social: Negotiate the specific cooperation described in the NPC entry. Skills: ['Persuade']; items: []. An interview and an offered favor; decline or failed persuasion leaves the ordinary route available. Success gains a more precise account with permission; failure withholds that cooperation, not every onward lead. Success -> END; failure -> lodging.

- lodging-ordinary: With Ro's standing fixture permission, lodging keeper Kit repeats an anonymous handover chronology. Kit remains when Ro leaves; no source identity or legal conclusion is disclosed. Skills: []; items: []. One delay; no special equipment or successful skill roll. Accept less precise evidence and the stated access limits. After a failed specialized attempt, take this separate limited lead and pay the ordinary delay. With Ro's standing fixture permission, lodging keeper Kit repeats an anonymous handover chronology. Kit remains when Ro leaves; no source identity or legal conclusion is disclosed. Success -> END; failure -> END.

Exit: Follow the next lead or leave with an explicitly incomplete report at the final scene.

## Expansion directions

- Labor noir: weigh source confidentiality against a persuasive public report; extra interviewing matters more than extra combat points.

- Maritime thriller: extend the inquiry offshore; research vessel access, weather and vehicle rules before granting a boat.

- Uncanny document: a receipt records an impossible arrival; keep this as an unresolved clue until the selected supernatural rules explain its effect.

## Acceptance walkthrough

Two original builds reuse `harbor/spec.json`: Reporter 280/280 occupation, 150 interest, Cargo clerk 280/280 occupation, 150 interest.

With no optional items or successful specialist checks, follow: ledger -> quay -> lodging -> END. Each transition uses the stated ordinary opportunity, pays delay and preserves only the limited evidence. At three delays move the cooperative witness off-site and use their designated public/custodian channel; never delete the onward route. This is a structural and prose walkthrough, not live play.

The player projection omits all scenes, clue destinations and the synthetic GM marker. Public item descriptions were reviewed separately. The tool checks registered fields; it cannot infer whether an item is historically available or whether text placed in a public field reveals an answer.



No-item walkthrough: ordinary scene 1 adds delay 1, ordinary scene 2 adds delay 2, ordinary scene 3 adds delay 3 and fires primary-NPC departure once. The named ordinary contacts persist, so the final report remains possible with the documented uncertainties.

Prior-failure walkthrough: a failed technical attempt adds delay 1 and retains the current scene; its ordinary alternative adds delay 2 and reaches scene 2. The next ordinary route reaches delay 3 and moves primary NPCs away. Scene 3 uses its named alternate contact, adds delay 4 and reaches END. This records access and information loss rather than converting failed technical work into success.

Consumable boundary: after the three allocated copies or statement leaves are used, the fourth written copy is unavailable; use the listed oral/custodian alternative or obtain an explicitly new allocation. The tool tests the stronger no-item case; it does not automatically decrement these consumables.
