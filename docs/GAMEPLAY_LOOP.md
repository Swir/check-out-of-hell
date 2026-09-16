# Gameplay Loop

CHECKOUT OF HELL is not intended to be an endless arena shooter. Every department
should combine a clear workplace objective with fast combat and escalating pressure.

## Prototype loop

The current two-map prototype implements the first complete version of that loop:

1. **Restore three breaker circuits** by finding three Breaker Fuse pickups.
2. **Survive the department** while store equipment attacks.
3. **Defeat the supervisor** (`NightManager` on MAP01, `RegionalManager` on MAP02).
4. When all three fuses are restored and the supervisor is dead, the shift clears and
   the map exits automatically after a short confirmation delay.

This is deliberately simple enough to validate the underlying systems before the maps
become larger, more decorated and objective-heavy.

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
enemies directly on top of the player.

## HUD contract

The current prototype overlay communicates only information needed for the loop:

- elapsed shift timer,
- current Overtime state,
- restored breakers (`0/3` through `3/3`),
- whether the current supervisor is still active,
- a short clock-out message when the level objective is complete.

The final HUD will use original art and a stronger supermarket-night-shift identity.

## Next gameplay step

Replace the flat MAP01 arena with a real `Closing Time` department flow: separated store
zones, breaker locations that require traversal, a powered shutter/gate objective,
environmental jokes/secrets and a supervisor encounter staged after the player restores
power.
