# Evidence dependency audit

Use `scripts/investigation.py` alongside `campaign_check.py`. The latter checks places and exits; this tool checks declared evidence-to-conclusion dependencies. Both are GM preparation aids, not proofs that prose is convincing or that players will solve a mystery.

## Contract

See [the original harbor example](../assets/examples/investigation.json). Schema 1 has `evidence` and `conclusions`, with globally unique IDs. Each record requires text and an explicit audience (`[]` GM-only, `["all"]` public, or player IDs).

- Evidence requires `available`: whether acquisition is possible in the scenario being audited. Audience separately records who has actually received that evidence. Keep undiscovered evidence GM-only even if it is available in the world.
- Conclusions require `essential` and `routes`. Routes are alternatives (OR); every ID within one route is required (AND). An ID may name evidence or another conclusion. Empty routes mean no declared support; empty AND groups are rejected.
- Conclusion text is a GM design assertion. A derivable conclusion is neither automatically revealed nor certified true. Keep world truth, evidence and player hypotheses distinct in prose. Hypotheses belong in the ledger's review notes, not as evidence seeds.
- A fixed-point traversal reports blocked conclusions, including unsupported cycles. Cycles with external evidence can resolve. Removing each available evidence item identifies single-evidence bottlenecks for currently derivable essential conclusions.

```powershell
python -X utf8 scripts/investigation.py assets/examples/investigation.json
python -X utf8 scripts/investigation.py assets/examples/investigation.json --unavailable shipping-log
python -X utf8 scripts/investigation.py assets/examples/investigation.json --knowledge-of pc1
python -X utf8 scripts/investigation.py assets/examples/investigation.json --player pc1
```

Default analysis assumes all available evidence could be acquired. `--knowledge-of` restricts seeds to evidence disclosed to one player; its output remains GM-only. `--player` exports only visible available evidence text, excluding IDs, routes, destinations, conclusions and extra fields. It cannot detect a secret mistakenly written into public text.

Exit codes: 0 means all declared essential conclusions are derivable, 1 means some are blocked, 2 means invalid input. Bottleneck warnings do not fail an otherwise solvable scenario. No mode changes the plan or session.

## Preparation walkthrough

1. Declare the essential conclusions and check whether each route actually supports its conclusion in the fiction; the script cannot do this semantic review.
2. Run the baseline. Remove one clue, close a location (mark its evidence unavailable in a private scenario copy), and model refusal of the hook by removing only the acquisitions that depend on accepting it.
3. For split parties, run each player's knowledge separately. Share evidence only after actual in-fiction communication; do not union their knowledge implicitly.
4. Repair bottlenecks with plausible independent acquisition methods or allow an explicit unresolved outcome. Never promise that all player choices must succeed.
5. Keep the location graph consistent with the acquisition plan. This schema does not model locks, travel time, skill checks or evidence automatically created by reaching a conclusion; review those separately.
