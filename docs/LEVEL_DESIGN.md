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
- no mandatory breaker inside the optional room, preserving route clarity,
- clearance-aware Overtime hazard anchors that stop creating fresh electrical hazards once the Night Manager is down,
- an original `CLOCK OUT` guide that appears near the front lanes only after supervisor clearance, pointing back toward the existing physical completion zone without changing the trigger.

The Staff Only room is deliberately a reward loop rather than a key hunt. Partial power gives the
player a useful side benefit before the main objective is complete, teaching that restoring store
systems can change the environment without making every side route mandatory.

The supervisor encounter is now a pressure sequence rather than one isolated monster spawn. Full
power activates two management-response anchors on opposite sides of the rear arena. Once the Night
Manager is defeated, surviving threats still matter on the run back to the registers, but new
management reinforcements and fresh Overtime floor hazards retire. The front-lane `CLOCK OUT` guide
then becomes visible, preserving tension while making the final workplace objective unambiguous.

Remaining Closing Time polish:
- complete an interactive target-Windows full-level pass with manual save/load, physical-controller and real-hardware performance confirmation,
- finish balance/sign-off on all three difficulty modes using that real playtest evidence,
- strengthen checkout-lane cover and sightlines only where the playtest shows a readability or pacing problem,
- keep any additional lighting/geometry reactions subordinate to combat readability rather than adding decoration for its own sake.

## MAP02 — Warehouse 13.5
Purpose: larger arena, heavier enemies and first boss-scale fight.

Current prototype includes:
- Security Price Scanners,
- Possessed Pallet Jacks,
- The Regional Manager prototype boss,
- access to Receipt Ripper, Price-Gun SMG and Turbo Can Launcher,
- all three breakers required before The Regional Manager can enter the fight,
- project-owned retail surfaces and an original department soundtrack.

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
