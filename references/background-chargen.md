# Background-aware character creation specifications

Trigger when a user describes an adventure's era, place, society or genre and needs creation rules, occupations or skill budgets. Research actively; do not wait for an explicit request to browse. This workflow supports any named system. The bundled arithmetic adapter currently validates **CoC7**; use the selected system's own tools for other systems, without translating its points into percentiles.

## 1. Establish the playable brief

Reuse the user's system/version, background and existing campaign decisions. Extract date or range, location, historical/alternate-history premise, tone, investigation/combat/social/survival emphasis, session length, party size, experience level and allowed material. Distinguish supplied facts from assumptions. Ask only for information that changes the rules: for example, whether the user wants mundane historical horror or Pulp heroes. Other uncertainties can remain labelled, reversible assumptions.

If no system is named, compare at most two or three suitable systems using the desired player activities, lethality, supernatural access and complexity. Recommend one with reasons; a provisional spec must name its assumed system. Never silently replace an already selected system. Historical dates do not determine skill budgets by themselves.

## 2. Research questions, not just the era's name

Search official rulebooks/errata and available local books, then publisher adventures with similar **period, region, genre or activity**. Read actual creation paragraphs, character sheets or pregenerated characters. A product description may establish setting relevance but cannot establish skill bases or point formulas. Prefer two comparators where available; one well-supported comparison plus an explicit gap is better than invented authority.

For history, use archives, museums, libraries, scholarship and contemporary sources, noting the source's date and geography. Investigate only facts that affect play: occupations and training, literacy/languages, travel and communication, institutions and access, equipment availability, money/credit and supply. A technology's invention does not prove widespread local ownership. A source about the fifteenth century does not establish tenth-century literacy. Record inference separately from explicit evidence.

Save source URL/title, publisher/author, edition, page or section, retrieval date, what was actually read and limits. Download lawful public samples into `index_root`; keep originals and extraction caches outside the skill. Use the PDF workflow to inspect ambiguous tables or filled fields. Treat forums as leads and proposed interpretations; confirm mechanical claims against the chosen edition.

## 3. Produce the adaptation ledger

For every change write: original rule and source → background/genre need → proposed treatment → mechanical cost → effect on character choice → verification case. Classify it as **unchanged rule, setting interpretation, existing supplement rule, or original house rule**. A pregen's final percentages do not reveal its allocation history: never reverse-engineer a universal budget from a high skill or special equipment.

Choose among retaining a skill, changing its fictional application, renaming it, splitting it, adding a specialty or removing an unavailable option. Specify base value, eligible occupation pools, interest eligibility, aliases and caps for every changed skill. Renaming preserves the old numeric rule unless a separately justified rule changes it. If reading/writing and spoken language are separated, define both and their access; EDU alone must not silently grant the new literacy skill. Avoid charging twice for two names describing the same capability.

Use the selected occupation's legal budget first. For an original occupation select an explicit formula, list its eligible skills and explain which established patterns support it. A changed cap or extra pool needs an explicit house-rule decision; do not declare it historically proven or universal. Separate an approved fixture profile from a player's unapproved proposal. Preserve an unmodified baseline comparison so the user can see what changed.

Do not infer competence or restrictions from gender, ethnicity, nationality or social category alone. Model relevant institutions, individual training and negotiated setting constraints. Offer playable exceptions with concrete fictional explanations. Historical disadvantage is not a reason to silently reduce attributes or impose a player's beliefs.

## 4. Deliver two distinct artifacts

Use [the specification template](../assets/templates/background-chargen.md). The **player specification** contains premise without spoilers, permitted concepts, generation method, occupations, formulas, skill changes/base values/caps, resources, wealth, equipment, languages, connections, team opportunities and final checklist. Give reasons players can understand without revealing the mystery.

The **GM dossier** contains the research and comparison ledger, source conflicts, rejected options, hidden scene needs, alternative clues, assumptions and verification report. Never export this by stripping a few headings from a secret document. Build the player document from an explicit field whitelist. `background_chargen.py --player` projects validated cards only, not the whole GM specification.

Show party capabilities as alternatives, not mandatory clue-solving builds. For example, access to a record might come from reading it, consulting its keeper or comparing a physical delivery trail. A role threshold is a design diagnostic, not a new rule or prerequisite for receiving essential information. Never require the skill that names the hidden culprit or supernatural answer.

## 5. Validate and revise

For each spec create two distinct, complete proposed characters: characteristics with generation evidence and age treatment, all allocated points and untrained bases, derived stats, languages, combat, resources, equipment ownership/cost, relationships and motivation. Show exact occupation and interest totals and unused points. Check caps, prerequisite training, forbidden options, currency, borrowed gear and team alternatives. Explicitly identify nonhistorical scenario allowances.

Run the numerical adapter only for its declared system. It validates the configured arithmetic and equipment allowlist; it does not authenticate sources or infer an item's history. A missing source or unresolved rule produces a **draft**, not false certification. Wrong edition fails. If the user wants a different system, return to that system's native creation rules.

The bundled [three cases and six cards](../assets/examples/background-chargen/README.md) are acceptance fixtures, not universal templates for all historical campaigns. Their approved house rules belong only to those fixtures. Test ordinary and adversarial inputs: budget overrun, unknown specialty, false base override, cap violation, anachronistic equipment, source missing, version mismatch and player export leakage. Live-player validation is outside scope.
