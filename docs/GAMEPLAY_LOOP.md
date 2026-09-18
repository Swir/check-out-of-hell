# Gameplay Loop

CHECKOUT OF HELL is not an endless arena shooter. Every department combines a clear workplace objective with fast combat, optional exploration and escalating supernatural retail pressure.

## Prototype loop

The current three-map prototype implements the core shift loop:

1. **Enter the department** and read the immediate workplace problem.
2. **Restore three breaker circuits** by finding three Breaker Fuse pickups.
3. **Activate the department-specific system** that full power makes useful when the level calls for one.
4. **Survive hostile store equipment** while Overtime raises enemy and environmental pressure.
5. **Exploit optional powered side routes** when partial power brings store systems back online.
6. **Defeat the supervisor** while management escalates its response.
7. **Return to the department exit/clock-out route** after management is cleared.

The maps intentionally use different staging:

- `MAP01 — Closing Time` spreads the breakers across left, right and rear store routes. The **Night Manager does not enter the floor until all three breakers are restored**. At `2/3`, the rear-left **Staff Only** security barrier powers down and opens an optional employee room containing an Employee of the Month Stash and one Corporate Compliance Memo. No mandatory breaker is hidden there.
- `MAP02 — Warehouse 13.5` restores three loading-bay circuits first. Full power then reveals a project-owned **Freight Lift Override** at the rear bay. **The Regional Manager remains off-floor until the player deliberately engages that control**, so MAP02 has a separate work action between power restoration and its boss response.
- `MAP03 — Frozen Foods` sends the player through alternating freezer aisles for three cold-chain breakers. Full power exposes a recovery cache and the existing power-gated **Night Manager** response. Four authored Overtime floor-hazard anchors pressure side/rear lanes, while the entry/clock-out approach stays clear enough to read during the final return.

## Breaker feedback

Each restored breaker produces immediate feedback instead of silently changing an inventory counter. The HUD reports the current power count while short power-restoration messages explain which route or system has changed. In Closing Time, `2/3` explicitly calls out Staff Only access and `3/3` unlocks a guaranteed Full-Power Emergency Cache on the approach to the arena. In Warehouse 13.5, the messages describe loading-bay power and the lift relay; `3/3` announces that the Freight Lift Override is available instead of pretending the boss itself has already arrived. Frozen Foods currently reuses the clear non-warehouse breaker language while its map geometry, department signs, cold-storage route and dedicated soundtrack carry the department identity.

## Warehouse 13.5 freight-lift sequence

MAP02's first distinct department objective is deliberately simple and readable:

1. restore all three warehouse circuits,
2. cross to the rear loading bay,
3. engage the newly powered Freight Lift Override,
4. survive The Regional Manager's arrival and two-phase attack kit,
5. return to the warehouse entry after supervisor clearance.

The lift-control spawner also supplies a department-local warehouse marker used by the normal HUD and optional Focus HUD. That marker and the lift-override inventory state are cleared only on a genuinely fresh department load; savegame restores preserve them. The lift control and Regional Manager spawn anchors are separated so interacting with the objective cannot immediately overlap the player with the boss.

Project-owned `FREIGHT ONLY` signage, restock clutter, slow failing fluorescents and wet-floor cones reinforce the loading-bay identity. They are non-blocking and placed away from the central breaker/lift/boss lane, so this presentation pass does not turn decoration into accidental combat cover.

A right-side **Damaged Goods** cage adds a separate optional tactical decision without changing that objective chain. Four solid, shootable stock piles built from project-owned box art seal a small reward nook. Breaking a useful gap costs ammunition but exposes a Damaged-Goods Label Crate and an Emergency Break Snack; no breaker, lift control or boss anchor is placed inside. The nearby Security Price Scanner remains outside the cage approach, so the route reads as an ammo-for-supplies choice rather than mandatory progression or accidental enemy containment.

## Frozen Foods sequence

MAP03 is a complete first-pass playable department rather than a placeholder:

1. enter through the front cold-storage approach,
2. restore three cold-chain circuits distributed across freezer side/rear routes,
3. use the optional full-power recovery cache if needed,
4. survive the power-gated Night Manager plus the existing deterministic management-response sequence,
5. keep moving as side-lane Overtime hazards activate during a long shift,
6. return to the front entry after supervisor clearance and clock out.

Four shelf barriers create freezer lanes without closing the central service route. Initial enemies, management response and Overtime anchors are kept away from the entry centerline, while paired project-owned `FROZEN FOODS` signs, safe retail clutter and the original **Compressor Choir** MIDI theme make the department visually/audibly distinct. Three optional Corporate Compliance Memos add a small exploration route.

A one-shot `FrozenDepartmentInitSpawner` clears only Corporate Memo progress carried into a fresh MAP03, then destroys itself. That makes the optional memo route department-local without adding a global event handler that could wipe progress after loading a save made inside Frozen Foods.

## Night Manager response sequence

Full power starts a staged rear-arena encounter in maps that use `CheckoutBossWaveSpawner`. The authored sequence is deterministic once all three breakers are restored:

| Time after full power | Reinforcement at each anchor |
| --- | --- |
| 0:15 | Angry Self-Checkout |
| 0:34 | Cart of Doom |
| 0:54 | Security Price Scanner |
| 1:16 | Possessed Pallet Jack |

The wider cadence gives every threat enough readable combat space. The sequence is separate from global Overtime, so a slow player can still experience both systems at once. Once the supervisor dies, unfinished management-response waves and fresh ambient Overtime reinforcements stop spawning; enemies already on the floor remain dangerous.

## Clock-out escape

Killing the supervisor does not complete the map automatically. Once all three breakers are restored and management is down, the department objective changes to its return leg. Closing Time shows `RETURN TO FRONT CHECKOUT`; fresh Overtime floor-hazard anchors retire at the same clearance point as reinforcement spawners, while a project-owned `CLOCK OUT` guide appears on the front-lane approach. The player still has to travel back into the existing checkout/timecard zone; the guide does not move, enlarge or bypass the completion trigger. Entering the zone confirms `TIMECARD ACCEPTED` and exits after a short completion beat.

Warehouse 13.5 uses the same physical front/entry completion region after its Regional Manager fight, but its HUD names the route as the warehouse entry so the level does not present supermarket-checkout wording during the loading-bay objective. Frozen Foods returns to the same front completion rule and reveals the existing non-blocking clock-out guide near its entry after supervisor clearance.

This creates a final movement objective and reinforces the core joke: even after defeating supernatural management, the employee still has to finish the shift correctly.

## Overtime

Overtime is a deterministic pressure director driven by elapsed map time.

| Elapsed shift time | State | Pressure |
| --- | --- | --- |
| 0:00–1:29 | SHIFT ACTIVE | Base encounter |
| 1:30–2:59 | STORE UNSTABLE | Angry Self-Checkout reinforcement pressure + warning layer |
| 3:00–4:29 | OVERTIME | Cart of Doom reinforcement pressure + active electrical floor hazards |
| 4:30+ | HELL RUSH | Frequent Possessed Pallet Jack pressure + faster hazard cadence |

Map designers place invisible `CheckoutOvertimeSpawner` and hazard anchors at authored locations. Reinforcements never appear directly on top of the player, and electrical hazards use a visible warning phase before damage. Scripted Overtime timings are intentionally shared by all difficulty modes so the player can learn the escalation language instead of fighting hidden random rules. In Closing Time, the environmental hazard schedule remains `90 / 135 / 180 / 212 / 244 / 270` seconds before entering a 20-second Hell Rush cadence; supervisor clearance retires any remaining anchors so the final route is pressured by survivors rather than newly created traps. Warehouse 13.5 uses the same readable schedule at two authored side-lane anchors, deliberately kept off the freight-lift/clock-out centerline and outside the Damaged Goods cage; those anchors retire on Regional Manager clearance through the same token gate. Frozen Foods uses four authored side/rear anchors kept away from the entry completion lane and reuses the same telegraph/cutoff rules.

## Difficulty modes

The prototype ships with three authored shift difficulties:

| Mode | Purpose | Combat tuning |
| --- | --- | --- |
| **Closing Crew** | forgiving first run / accessibility-friendly baseline | +25% ammo, -25% incoming damage, +20% healing, enemies at 90% health |
| **Graveyard Shift** | intended default | baseline ammo, damage, healing and enemy health |
| **Corporate Hell** | high-pressure replay | -15% ammo, +25% incoming damage, -15% healing, enemies at 115% health |

Difficulty changes resource forgiveness and combat durability rather than silently speeding scripted hazards or enabling opaque respawn rules. `Graveyard Shift` is the default. `Corporate Hell` requires an explicit confirmation before clocking in.

## Exploration and joke interactions

Closing Time includes three optional Corporate Compliance Memos, a powered Staff Only side route, Employee of the Month reward stash, Emergency Break Snacks, department signage and safe environmental clutter. Warehouse 13.5 adds the optional breakable Damaged Goods cage and Lockout/Tagout safety choice. Frozen Foods adds its own three-memo route plus side-lane Emergency Break Snacks and cold-storage department dressing. Optional rewards must stay useful or funny without becoming disguised mandatory progression.

## HUD contract

The final-layout prototype HUD keeps critical information separated into readable zones:

- current department-aware objective and route hint,
- restored breakers (`0/3` through `3/3`),
- optional Corporate Memo progress in Closing Time/Frozen Foods or Freight Lift state in Warehouse 13.5,
- elapsed shift timer and `06:00` clock-out target,
- current Overtime state, patterned pressure meter and next escalation countdown,
- worker health plus label, receipt and can reserves,
- short power, memo and clock-out feedback banners.

Important Overtime and health states use text/pattern feedback in addition to color.

## Closing Time progression contract

MAP01 has a deliberately testable route contract:

- the player begins in the front entrance zone,
- retail fixtures split the floor into traversal lanes,
- breakers pull the player into left, right and rear routes,
- after two breakers, the optional Staff Only room opens,
- the optional room contains rewards but no mandatory breaker,
- after `3/3`, the Full-Power Emergency Cache and Night Manager encounter become available,
- two rear boss-wave anchors feed the authored reinforcement sequence,
- supervisor defeat stops new reinforcement and floor-hazard creation, reveals the front-lane `CLOCK OUT` guide and changes the objective to returning to the front checkout,
- entering the unchanged front timecard zone completes the shift.

Static contracts protect the layout, optional route, pacing, HUD, Overtime hazards, post-boss guide and boss/escape rules. Windows CI additionally asks the pinned GZDoom runtime to parse the packaged prototype.

## Warehouse 13.5 progression contract

MAP02 has a separate testable route contract:

- exactly three breaker fuses remain mandatory,
- a single lift-control anchor becomes active only at full power,
- the lift override must be collected before the existing Regional Manager spawner can fire,
- the control and boss anchors remain separated by a safe readable gap,
- one right-side optional cage is sealed by exactly four breakable project-owned stock piles,
- the cage contains useful label/health rewards but no breaker, lift control or boss anchor,
- two authored Overtime hazard anchors remain on side lanes, outside the objective centerline and optional cage, and retire after supervisor clearance,
- HUD and Focus HUD states stay synchronized with the warehouse marker and lift token,
- generated lift/freight signage and the MAP02 environment layer are present in the packaged PK3,
- direct Regional Manager pre-placement remains forbidden.

`tools/test_warehouse_lift_objective_contract.py` and the shared Overtime hazard contract protect these rules in CI alongside the existing Regional Manager asset/behavior contract.

## Frozen Foods progression contract

MAP03 has its own packaged gameplay contract:

- exactly three breaker fuses remain mandatory,
- exactly one fresh-entry memo initializer clears carried optional memo progress and then self-retires,
- exactly one power-gated Night Manager spawner, one management-response anchor, one full-power recovery cache and one post-clear clock-out guide remain authored,
- three optional Corporate Compliance Memos stay outside mandatory progression,
- freezer shelving keeps a central readable service lane instead of regressing to a flat empty arena,
- paired project-owned Frozen Foods signs and safe environment props remain in the map layer,
- exactly four authored environmental Overtime anchors stay away from the entry/clock-out lane,
- `D_COH03` is generated deterministically, wired through MAPINFO and packaged with MAP03,
- direct Night Manager pre-placement remains forbidden.

`tools/test_frozen_foods_contract.py`, the shared music contract and pinned-engine parser protect these rules in CI.

## Next gameplay step

Closing Time still needs a genuine end-to-end Windows playtest before it can be called fully polished. The next major validation pass should focus on practical save/load behavior, balance across all three difficulties, controller/accessibility behavior, real-hardware performance and any remaining encounter or route friction found during real play. Warehouse 13.5 and Frozen Foods remain intentionally short of polished-level claims until their routes and encounter pacing receive the same level of interactive evidence.
