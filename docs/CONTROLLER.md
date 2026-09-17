# Controller support

CHECKOUT OF HELL uses GZDoom's standard controller input layer instead of shipping a custom driver or forcing a private binding scheme. The project targets the pinned GZDoom `g4.14.2` runtime and exposes the controls that matter to the current game loop directly in its own options submenu.

## In-game setup

Open **Options → CHECKOUT OF HELL Controller**.

The project menu exposes remappable entries for:

- primary fire and alternate fire,
- use / interact,
- jump and crouch,
- run / sprint,
- previous and next weapon,
- automap.

The same menu links to GZDoom's **Device / stick setup** and **Full control bindings** screens for controller selection, axes, sensitivity, dead zones and any additional engine-level binding. Existing player bindings are never overwritten by the mod.

## Engine default baseline

On a fresh compatible GZDoom controller configuration, the engine's standard Xbox/PlayStation-style baseline maps the main actions approximately as follows. Physical button labels can differ by controller and SDL mapping, and an existing user configuration can override every binding.

| Gameplay action | GZDoom default baseline |
| --- | --- |
| Move | Left stick |
| Look / turn | Right stick |
| Primary fire | Right trigger / R2 |
| Alternate fire | Left trigger / L2 |
| Use / interact | A / Cross |
| Jump | Y / Triangle |
| Crouch toggle | Left-stick click / L3 |
| Previous / next weapon | Left / right shoulder |
| Automap | D-pad up |
| Main menu | Start / Options |
| Pause | Back / View / Share-equivalent |

Current mandatory objectives do not require a controller-only custom command: breaker fuses and resources are pickups, combat uses standard fire/movement actions, and the Closing Time clock-out objective is completed by physically returning to the front lanes after supervisor clearance. `Use / interact` remains exposed for normal GZDoom interactions and future authored machinery without creating a hidden keyboard dependency.

## Restrained weapon haptics

Signature player weapon cues opt into GZDoom's built-in rumble profiles:

| Weapon | Cue | Rumble profile |
| --- | --- | --- |
| Emergency Mop | `coh/mopswing` | `MEDIUM` |
| Receipt Ripper | `coh/ripperfire` | `LIGHT` |
| Price-Gun SMG | `coh/pricefire` | `SUBTLE` |
| Turbo Can Launcher | `coh/canlaunch` | `HEAVY` |

These mappings add feedback only when the runtime and connected controller support haptics and the player's GZDoom haptics settings permit it. Enemy, ambient, Overtime and alarm cues are intentionally not mapped to rumble, avoiding constant vibration during prolonged combat. Haptics never alter damage, timing, objectives or difficulty.

## Validation and demo gate

CI checks the dedicated controller menu, standard-action bindings, the four signature haptic mappings and their packaged PK3 copies. The pinned Windows GZDoom parser job then validates the actual `MENUDEF`/`SNDINFO` syntax as part of the current package.

This automated support pass is **not** a claim that every controller model has been physically certified. Before a public demo, the target-Windows interactive sign-off still requires a real-controller playtest covering movement/look, all four signature weapons, weapon cycling, pause/menu navigation, save/load and the complete Closing Time objective route.
