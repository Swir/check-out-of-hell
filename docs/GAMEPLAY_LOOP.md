# Gameplay Loop

CHECKOUT OF HELL is not an endless arena shooter. Every department combines a clear workplace objective with fast combat, optional exploration and escalating supernatural retail pressure.

## Prototype loop

The current two-map prototype implements the core shift loop:

1. **Enter the department** and read the immediate workplace problem.
2. **Restore three breaker circuits** by finding three Breaker Fuse pickups.
3. **Survive hostile store equipment** while Overtime raises enemy and environmental pressure.
4. **Exploit optional powered side routes** when partial power brings store systems back online.
5. **Defeat the supervisor** while management escalates its response.
6. **Return to the front checkout** and physically clock out after the supervisor is dead and power is restored.

The maps intentionally use different staging:

- `MAP01 — Closing Time` spreads the breakers across left, right and rear store routes. The **Night Manager does not enter the floor until all three breakers are restored**. At `2/3`, the rear-left **Staff Only** security barrier powers down and opens an optional employee room containing an Employee of the Month Stash and one Corporate Compliance Memo. No mandatory breaker is hidden there.
- `MAP02 — Warehouse 13.5` also requires all three breakers before **The Regional Manager** arrives. The boss is created by a dedicated spawner rather than being active from map start, preserving the restore-power-before-management rule.

## Breaker feedback

Each restored breaker produces immediate feedback instead of silently changing an inventory counter. The HUD reports `POWER 1/3`, `2/3` and `3/3`, while short power-restoration messages explain which route or system has changed. At `2/3`, Staff Only access is explicitly called out. At `3/3`, supervisor access is restored and Closing Time unlocks a guaranteed Full-Power Emergency Cache on the approach to the arena.

## Night Manager response sequence

Full power starts a staged rear-arena encounter in `MAP01`. Two `CheckoutBossWaveSpawner` anchors flank the supervisor area and begin a deterministic management-response sequence once all three breakers are restored:

| Time after full power | Reinforcement at each anchor |
| --- | --- |
| 0:15 | Angry Self-Checkout |
| 0:34 | Cart of Doom |
| 0:54 | Security Price Scanner |
| 1:16 | Possessed Pallet Jack |

The wider cadence gives every threat enough readable combat space. The sequence is separate from global Overtime, so a slow player can still experience both systems at once. Once the supervisor dies, unfinished management-response waves and fresh ambient Overtime reinforcements stop spawning; enemies already on the floor remain dangerous.

## Clock-out escape

Killing the supervisor does not complete the map automatically. Once all three breakers are restored and management is down, the HUD changes to `RETURN TO FRONT CHECKOUT`. The player must travel back to the front checkout/timecard zone. Entering it confirms `TIMECARD ACCEPTED` and exits after a short completion beat.

This creates a final movement objective and reinforces the core joke: even after defeating supernatural management, the employee still has to clock out correctly.

## Overtime

Overtime is a deterministic pressure director driven by elapsed map time.

| Elapsed shift time | State | Pressure |
| --- | --- | --- |
| 0:00–1:29 | SHIFT ACTIVE | Base encounter |
| 1:30–2:59 | STORE UNSTABLE | Angry Self-Checkout reinforcement pressure + warning layer |
| 3:00–4:29 | OVERTIME | Cart of Doom reinforcement pressure + active electrical floor hazards |
| 4:30+ | HELL RUSH | Frequent Possessed Pallet Jack pressure + faster hazard cadence |

Map designers place invisible `CheckoutOvertimeSpawner` and hazard anchors at authored locations. Reinforcements never appear directly on top of the player, and electrical hazards use a visible warning phase before damage. Scripted Overtime timings are intentionally shared by all difficulty modes so the player can learn the escalation language instead of fighting hidden random rules.

## Difficulty modes

The prototype now ships with three authored shift difficulties:

| Mode | Purpose | Combat tuning |
| --- | --- | --- |
| **Closing Crew** | forgiving first run / accessibility-friendly baseline | +25% ammo, -25% incoming damage, +20% healing, enemies at 90% health |
| **Graveyard Shift** | intended default | baseline ammo, damage, healing and enemy health |
| **Corporate Hell** | high-pressure replay | -15% ammo, +25% incoming damage, -15% healing, enemies at 115% health |

Difficulty changes resource forgiveness and combat durability rather than silently speeding scripted hazards or enabling opaque respawn rules. `Graveyard Shift` is the default. `Corporate Hell` requires an explicit confirmation before clocking in.

## Exploration and joke interactions

Closing Time currently includes three optional Corporate Compliance Memos, a powered Staff Only side route, Employee of the Month reward stash, Emergency Break Snacks, department signage and safe environmental clutter. Optional rewards must stay useful or funny without becoming disguised mandatory progression.

## HUD contract

The final-layout prototype HUD keeps critical information separated into readable zones:

- current objective and route hint,
- restored breakers (`0/3` through `3/3`),
- optional Corporate Memo progress,
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
- supervisor defeat stops new reinforcement creation and changes the objective to returning to the front checkout,
- entering the front timecard zone completes the shift.

Static contracts protect the layout, optional route, pacing, HUD, Overtime hazards and boss/escape rules. Windows CI additionally asks the pinned GZDoom runtime to parse the packaged prototype.

## Next gameplay step

Closing Time still needs a genuine end-to-end Windows playtest before it can be called fully polished. The next major validation pass should focus on practical save/load behavior, balance across all three difficulties, controller/accessibility behavior and any remaining encounter or route friction found during real play.
