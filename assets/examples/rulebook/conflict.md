# Glass Engine — conflicting rules repaired

All source passages are synthetic test inputs. The latest design decision is explicit within this fixture; without that authority the skill would propose alternatives and retain a material open issue.

| Input location | Exact conflicting proposition | Evidence weight |
|---|---|---|
| Old creation chapter C-2, revision 1 | Maximum charge equals Focus times two | Older rule |
| New designer decision D-7, revision 2 | Every battery holds four charge; Focus changes precision only | Latest explicit synthetic decision |
| Old item example I-3 | Recharge at three charge grants two, ending at five | Older example violates new maximum |
| Old character card K-1 | Focus 3, charge 6/6 | Dependent obsolete card |

No existing game system is named or needed. Preserve the terms Focus and charge. Candidate A retains scaled batteries and rejects D-7; candidate B fixes capacity at four and changes all callers. Select B only because D-7 explicitly governs the fixture. The manifest's conflicting `battery.maximum` claims reproduce the numerical disagreement; the checker cannot infer D-7's authorial authority.

## Repaired rules — battery revision 2

A battery starts with four charge and holds integer charge from 0 to 4. Focus does not change capacity. Before firing the precision tool, spend one charge; at zero firing is unavailable and spends no action. The player may instead use the mundane tool without this bonus. The host confirms a legal target before payment. A shot's precision uses Focus in the existing precision procedure, whose complete resolution remains outside this narrow battery repair. Do not claim this battery chapter alone is a complete game.

Recharge requires a prepared station and one action. Add two charge, clamped to four. At full charge it is legal but gains nothing and still uses the action. No other action refunds charge. Recharging may repeat while the station is available; this is intentional renewable supply paid in actions, not a claim that all recharge cycles are exploits. Concurrent payments resolve in declared action order; reserve no charge for a shot already cancelled before payment.

Updated table: initial 4, minimum 0, maximum 4, shot cost 1, recharge +2, overflow discarded. Updated card: Focus 3, charge 4/4. Updated example: start at 3; recharge gives min(4,3+2)=4, next legal shot leaves 3. At zero, firing fails without a negative balance.

Migration: reject loading revision-1 capacity as current. After the user accepts the revision, reduce current charge to min(old current,4) and set maximum 4, preserving Focus. An old 6/6 becomes 4/4; old 1/6 becomes 1/4. Do not restore spent capacity or silently migrate a running game just because a proposed rulebook changed.

## Dependency and verification record

Changed canonical ID: battery, revision 1 to 2. Dependent artifacts: creation, equipment, character card, worked example and quick reference. Re-read every caller, replace the old formula, update explicit revision bindings, then recalculate examples. The companion [before manifest](conflict/before.json) retains contradictory claims and an open material issue. The [after manifest](conflict/after.json) binds the repaired files and records resolution.

Expected checks: before fails on stale binding/conflicting capacity/open issue; after passes explicit structure. `--changed battery` reports all five callers. Removing the worked-example file or restoring its old revision must fail. Paper boundary calculations verify zero, overflow and both migration examples. No semantic checker or full-game certification is claimed. The repaired source files are short affected excerpts, not a fabricated complete original rulebook.
