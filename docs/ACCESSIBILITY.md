# Accessibility

CHECKOUT OF HELL is a fast retro FPS, so accessibility work focuses on keeping objectives and combat pressure readable without hiding the game's timing or changing its authored difficulty rules.

## In-game options

Open **Options → CHECKOUT OF HELL Accessibility**.

- **Focus HUD** — adds a compact high-contrast text block with the current objective, breaker/memo counts and Overtime pressure. This is supplemental to the normal HUD and does not change gameplay.
- **Large warnings** — adds larger center-screen text for critical health, Overtime and Hell Rush pressure. Warnings use words as well as color.

Both options are player-local and disabled by default.

## Sensory readability baseline

The standard HUD communicates Overtime state through labels and a pressure pattern in addition to color. Critical health also has an explicit text warning.

Failing fluorescent props intentionally use a slower light-change cycle instead of the previous rapid two-tic flashes. The atmosphere remains unstable, but the default presentation avoids using a rapid strobe as a gameplay signal.

## Current limitations

This is an implemented first accessibility pass, not an accessibility certification. Controller support and a dedicated performance pass are still open demo-readiness tasks, and a final interactive Windows playtest is still required before a public demo can be approved.

If a future mechanic depends on color, sound or flashing alone, it should gain a redundant text/pattern/telegraph path before release.
