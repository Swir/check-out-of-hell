# Level Design Direction

## MAP01 — Closing Time
Purpose: first structured department flow, weapon onboarding and readable objective staging.

Current prototype includes:
- a larger supermarket floor than the original arena,
- front entrance spawn zone,
- internal aisle dividers and checkout-counter barriers,
- left, right and rear breaker routes,
- three Overtime reinforcement anchors spread across the floor,
- Security Price Scanner crossfire near the rear route,
- Night Manager spawned only after all three breakers are restored,
- two dedicated rear supervisor-response anchors that escalate through Self-Checkout, Cart, Scanner and Pallet Jack waves,
- contextual HUD task text that moves from power restoration to supervisor clearance and then a return to front checkout,
- a physical front checkout/timecard completion zone instead of automatic post-boss exit,
- short visible feedback after each breaker is restored,
- an optional rear-left Staff Only room with a physical security barrier,
- Staff Only access unlocking at `2/3` breakers instead of waiting for full power,
- an `Employee of the Month Stash` reward inside the optional room,
- no mandatory breaker inside the optional room, preserving route clarity.

The Staff Only room is deliberately a reward loop rather than a key hunt. Partial power gives the
player a useful side benefit before the main objective is complete, teaching that restoring store
systems can change the environment without making every side route mandatory.

The supervisor encounter is now a pressure sequence rather than one isolated monster spawn. Full
power activates two management-response anchors on opposite sides of the rear arena. After the
Night Manager is defeated, surviving threats remain relevant because the player must fight back to
the front checkout and clock out before the map advances.

Next polish:
- entrance shutters visibly slam shut behind the player,
- replace temporary Staff Only barrier visuals with original shutter/sign art,
- stronger authored checkout-lane cover and sightlines,
- authored lighting changes for each breaker state,
- PA announcements react to breaker restoration, supervisor arrival, reinforcement waves and clock-out,
- original signs, props, lighting and retail textures,
- stronger authored Night Manager arena geometry around the two response anchors,
- original Night Manager presentation instead of runtime placeholder visuals.

## MAP02 — Warehouse 13.5
Purpose: larger arena, heavier enemies and first boss-scale fight.

Current prototype includes:
- Security Price Scanners,
- Possessed Pallet Jacks,
- The Regional Manager placeholder boss,
- access to Receipt Ripper, Price-Gun SMG and Turbo Can Launcher.

Planned polish:
- moving pallet hazards,
- flickering warehouse lights,
- vertical shelf routes,
- breakable stock piles,
- hidden staff-room shortcut,
- a dedicated objective sequence so MAP02 no longer shares MAP01's simple breaker contract verbatim.

## Future departments

### MAP03 — Frozen Foods
Cold-storage combat where slippery routes, failing refrigeration and freezer-door timing
become readable hazards instead of random punishment.

### Electronics
Security systems, display walls and hostile demo hardware create sightline and alarm puzzles.

### Customer Service
Queue barriers, returns counters and escalating complaint-themed encounters create a tighter,
more comedic combat space before management access opens.

### Management Floor
The campaign's corporate nightmare: cleaner geometry, increasingly absurd executive hazards,
and the final route toward clocking out at 06:00.

## Design rule
Every room should have at least one gameplay joke that still works as a useful combat mechanic.
Humor must not replace readability, and progression gates must be visually understandable without
forcing the player to read long instructions during combat.
