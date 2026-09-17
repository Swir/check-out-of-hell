# Accessibility — CHECKOUT OF HELL

CHECKOUT OF HELL treats readability as part of combat design. The first accessibility pass keeps the Overtime system legible without making the player decode color alone or endure repeated high-intensity warning flashes.

## In-game accessibility menu

Open **Options → CHECKOUT OF HELL Accessibility**. The project surfaces stable GZDoom settings that are immediately useful during play:

- **UI scale** — enlarges engine UI elements and menus.
- **Notification text scale** — enlarges engine notifications independently of the general UI scale.
- **Crosshair scale** — makes the aiming reference easier to see.
- **Center notifications** — keeps engine notifications in a predictable central position.
- **Reduce pulsing notifications** — disables GZDoom's pulsing notification-text effect.
- **Intermission subtitles** — exposes the engine subtitle control for supported intermission content.
- Direct links to the full **Display / UI**, **Controller / input**, and **Audio** menus are included so players do not need to hunt through unrelated menus.

These settings are native GZDoom archived CVARs. The project does not shadow them with a second configuration system, so the values persist using the engine's normal configuration behavior.

## Overtime visual-safety pass

Overtime warning actors previously used bright rendering through most of their visible lifetime. They now use a single short bright pulse followed by normal-lit warning frames. The alarm sound, telegraph duration, electrical-arc timing, damage radius and Overtime cadence are unchanged.

The HUD continues to communicate Overtime state with explicit text (`SHIFT ACTIVE`, `STORE UNSTABLE`, `OVERTIME`, `HELL RUSH`) and a textual pressure meter in addition to color. Objective and route guidance likewise remain text-first.

## Scope and remaining work

This is a practical first accessibility pass, not a claim that every accessibility need is solved. The public demo still requires target-Windows playtesting, controller validation and a performance pass. Future passes may add more project-specific sensory controls if playtesting shows they are needed.

Accessibility changes must not hide gameplay information, alter objective timing, or make hazards less predictable.
