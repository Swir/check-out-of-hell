# Gameplay Loop

CHECKOUT OF HELL is not intended to be an endless arena shooter. Every department
should combine a clear workplace objective with fast combat and escalating pressure.

## Prototype loop

The current two-map prototype implements the first complete version of that loop:

1. **Restore three breaker circuits** by finding three Breaker Fuse pickups.
2. **Survive the department** while hostile store equipment and Overtime reinforcements attack.
3. **Exploit optional powered side routes** when partial power brings store systems back online.
4. **Defeat the supervisor**.
5. When all three fuses are restored and the supervisor is dead, the shift clears and
   the map exits automatically after a short confirmation delay.

The maps intentionally use different progression staging:

- `MAP01 — Closing Time` spreads the breakers across left, right and rear store routes.
  The **Night Manager does not enter the floor until all three breakers are restored**.
  This makes power restoration a real prerequisite instead of an optional pickup sweep.
  After `2/3` breakers, a rear-left **Staff Only** security barrier powers down and opens
  an optional employee room containing an `Employee of the Month Stash`. No mandatory
  breaker is hidden inside that room, so the reward remains optional rather than becoming
  a disguised progression lock.
- `MAP02 — Warehouse 13.5` currently keeps The Regional Manager active from the start,
  creating a more chaotic arena-style prototype while its dedicated objective flow is built.

## Breaker feedback

Each restored breaker now causes immediate visible feedback instead of silently changing an
inventory counter. The player gets a short power-restoration banner and a teleport-fog pulse.
At `2/3`, the banner explicitly announces that **Staff Security is online**; at `3/3`, it
announces full power and supervisor access. The effect is deliberately short so combat remains
readable.

This is still prototype presentation. Final feedback should become authored lighting changes,
original breaker sounds, PA announcements and original environment art rather than relying on
runtime-placeholder effects.

## Overtime

Overtime is a pressure director driven by elapsed map time.

| Elapsed shift time | State | Prototype pressure |
| --- | --- | --- |
| 0:00–1:29 | SHIFT ACTIVE | Base encounter |
| 1:30–2:59 | STORE UNSTABLE | Angry Self-Checkout reinforcements |
| 3:00–4:29 | OVERTIME | Faster Cart of Doom reinforcements |
| 4:30+ | HELL RUSH | Frequent Possessed Pallet Jack reinforcements |

Map designers place invisible `CheckoutOvertimeSpawner` markers at safe reinforcement
locations. The director keeps escalation deterministic and readable rather than spawning
enemies directly on top of the player. MAP01 uses three reinforcement anchors so the
larger floor can pressure multiple routes without concentrating every spawn in one corner.

## HUD contract

The current prototype overlay communicates only information needed for the loop:

- elapsed shift timer,
- current Overtime state,
- restored breakers (`0/3` through `3/3`),
- supervisor state,
- a contextual task line (`RESTORE ALL BREAKERS`, `CLEAR THE SUPERVISOR`, `CLOCK OUT`),
- short breaker/power restoration banners,
- a short clock-out message when the level objective is complete.

The final HUD will use original art and a stronger supermarket-night-shift identity.

## Closing Time progression contract

MAP01 has a deliberately testable route contract:

- the player begins in the front entrance zone,
- internal blocking retail fixtures split the floor into traversal lanes,
- one breaker pulls the player into the left route,
- one breaker pulls the player into the right route,
- one breaker sits in the rear route,
- after two breakers, the optional Staff Only side room opens,
- the optional room contains a comedy reward but no mandatory breaker,
- the Night Manager is represented by a `CheckoutManagerSpawner`, not a pre-placed boss,
- after `3/3` breakers, the spawner creates Night Manager and the objective changes to clearing the supervisor.

`tools/test_closing_time_layout.py` protects the main route rules. `tools/test_staff_room_contract.py`
protects the optional room geometry, two-breaker power gate, reward placement and the guarantee
that the side room cannot accidentally become mandatory.

## Next gameplay step

Replace the temporary powered-barrier presentation with original shutter/sign art and authored
lighting, then add an entrance-shutter opening beat and PA reactions. After that, MAP01 needs a
more deliberate Night Manager encounter space and original combat presentation before it can be
considered a vertical-slice-quality level.
