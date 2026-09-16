# Gameplay Loop

CHECKOUT OF HELL is not intended to be an endless arena shooter. Every department
should combine a clear workplace objective with fast combat and escalating pressure.

## Prototype loop

The current two-map prototype implements the first complete version of that loop:

1. **Restore three breaker circuits** by finding three Breaker Fuse pickups.
2. **Survive the department** while hostile store equipment and Overtime reinforcements attack.
3. **Exploit optional powered side routes** when partial power brings store systems back online.
4. **Defeat the supervisor** while the department escalates its management response.
5. **Return to the front checkout** and clock out after the supervisor is dead and power is restored.

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

Each restored breaker causes immediate visible feedback instead of silently changing an
inventory counter. The player gets a short power-restoration banner and a teleport-fog pulse.
At `2/3`, the banner explicitly announces that **Staff Security is online**; at `3/3`, it
announces full power and supervisor access. The effect is deliberately short so combat remains
readable.

This is still prototype presentation. Final feedback should become authored lighting changes,
original breaker sounds, PA announcements and original environment art rather than relying on
runtime-placeholder effects.

## Night Manager response sequence

Full power now starts a staged rear-arena encounter in `MAP01` rather than only spawning the
Night Manager. Two `CheckoutBossWaveSpawner` anchors flank the supervisor area and begin their
own deterministic management-response sequence once all three breakers are restored:

| Time after full power | Reinforcement at each anchor |
| --- | --- |
| 0:12 | Angry Self-Checkout |
| 0:26 | Cart of Doom |
| 0:42 | Security Price Scanner |
| 0:58 | Possessed Pallet Jack |

The sequence is deliberately predictable enough to learn while still forcing the player to move.
It is separate from global Overtime, so a slow player can experience both pressure systems at once.
Future polish should add original PA announcements and arena lighting cues before each wave.

## Clock-out escape

Killing the supervisor no longer completes the map automatically. Once all three breakers are
restored and the supervisor is dead, the HUD changes to `RETURN TO FRONT CHECKOUT`. The player
must travel back to the entrance checkout/timecard zone at the front of the store. Entering that
zone confirms `TIMECARD ACCEPTED` and exits after a short one-second completion beat.

This creates a final movement objective and lets surviving enemies matter after the boss fight.
It also reinforces the core joke: even after defeating supernatural management, the employee still
has to clock out properly.

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
- a contextual task line (`RESTORE ALL BREAKERS`, `CLEAR THE SUPERVISOR`, `RETURN TO FRONT CHECKOUT`),
- short breaker/power restoration banners,
- explicit timecard acceptance feedback when the player reaches the front checkout.

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
- after `3/3` breakers, the spawner creates Night Manager and two rear boss-wave anchors activate,
- supervisor defeat changes the objective to returning to the front checkout instead of auto-exiting.

`tools/test_closing_time_layout.py` protects the main route rules. `tools/test_staff_room_contract.py`
protects the optional room geometry and power gate. `tools/test_boss_escape_contract.py` protects
the staged supervisor waves, rear-arena placement and front-checkout completion contract.

## Next gameplay step

Replace the temporary powered-barrier presentation with original shutter/sign art and authored
lighting, then add original PA cues for full power, each boss reinforcement wave and timecard
acceptance. After that, the Night Manager needs original presentation and a stronger authored
arena layout before `Closing Time` can be considered vertical-slice quality.
