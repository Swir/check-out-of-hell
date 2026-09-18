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
- an original `CLOCK OUT` guide that appears near the front lanes only after supervisor clearance, pointing back toward the existing physical completion zone without changing the trigger,
- a conservative combat-readability pass that clears the front-to-rear center strip of initial hostile/reinforcement anchors, moves management-response spawns to the rear flanks and mirrors non-blocking Lane 06 wayfinding at the front approach.

The Staff Only room is deliberately a reward loop rather than a key hunt. Partial power gives the
player a useful side benefit before the main objective is complete, teaching that restoring store
systems can change the environment without making every side route mandatory.

The supervisor encounter is now a pressure sequence rather than one isolated monster spawn. Full
power activates two management-response anchors on opposite rear flanks. Their authored timing is
unchanged, but the spatial pass avoids spawning that sequence on the central supervisor sightline.
Once the Night Manager is defeated, surviving threats still matter on the run back to the registers,
but new management reinforcements and fresh Overtime floor hazards retire. The front-lane `CLOCK OUT`
guide then becomes visible, preserving tension while making the final workplace objective unambiguous.

The readability pass deliberately changes spawn placement and non-blocking wayfinding only. It does
not move solid checkout geometry, objective triggers, breaker routes or combat timing without actual
playtest evidence.

Remaining Closing Time polish:
- complete an interactive target-Windows full-level pass with manual save/load, physical-controller and real-hardware performance confirmation,
- finish balance/sign-off on all three difficulty modes using that real playtest evidence,
- change solid checkout cover or sightline geometry only where the playtest shows a readability or pacing problem,
- keep any additional lighting/geometry reactions subordinate to combat readability rather than adding decoration for its own sake.

## MAP02 — Warehouse 13.5
Purpose: heavier equipment pressure, a real loading-bay work task and the first boss-scale corporate escalation.

Current prototype includes:
- Security Price Scanners,
- Possessed Pallet Jacks,
- The Regional Manager prototype boss,
- access to Receipt Ripper, Price-Gun SMG and Turbo Can Launcher,
- three warehouse breakers that restore the loading-bay circuits,
- a project-owned `Freight Lift Override` that appears only after all three circuits are live,
- The Regional Manager held off-floor until the player deliberately engages that powered lift control,
- warehouse-specific HUD/Focus HUD objective states for breakers, lift activation, Regional Management and the return-to-entry leg,
- project-owned freight signage, restock clutter, readable slow-failing lights and loading-bay dressing placed off the central objective/combat lane,
- an optional damaged-goods cage whose four project-owned shootable stock piles trade ammunition for a label stash and break snack without hiding mandatory progression,
- an optional full-power `Lockout/Tagout Permit` on the opposite rear side lane that isolates future Warehouse electrical floor arcs without disabling hostile Overtime reinforcements or management pressure,
- project-owned retail surfaces and an original department soundtrack.

The first Warehouse 13.5 objective sequence is now explicit: restore all three circuits, cross to the
rear loading bay, engage the freight-lift override, survive the Regional Manager response, then return
to the warehouse entry to finish the department. The lift control is separated from the boss spawn
anchor so interacting with the objective cannot immediately overlap the player with the boss. The
extra loading-bay props are non-blocking and deliberately stay out of the central route so the level
gains identity without sacrificing readable combat.

A right-side damaged-goods nook adds the first breakable-stock tactical choice. Four solid, shootable
stock piles seal the opening; breaking any useful gap costs ammunition but opens access to optional
labels and health. The existing Security Price Scanner remains outside the cage approach, and no
breaker, lift control or boss anchor is inside the nook. The joke therefore changes resource routing
without becoming a key hunt or muddying the central lift/Regional Manager sightline.

The left-side Lockout/Tagout station adds a second workplace choice after full power. Taking the permit
retires only future Warehouse electrical floor arcs, representing a useful system repair rather than a
magic combat-off button. Ambient Overtime enemy reinforcements, the freight-lift objective, management
response waves and The Regional Manager all remain active, so the player trades a short detour for a
safer floor while preserving the department's combat pressure.

Remaining Warehouse 13.5 polish:
- authored moving pallet hazards that communicate their lane before becoming dangerous,
- stronger vertical shelf routes instead of a mostly flat combat floor,
- a hidden staff-room shortcut/reward loop,
- department-specific encounter pacing around the lift activation and Regional Manager phases,
- full interactive balance/readability sign-off before the level is called polished.

## MAP03 — Frozen Foods
Purpose: first playable cold-storage department with readable aisle routing, refrigeration atmosphere and a breaker → compressor reset → management → clock-out loop.

Current prototype includes:
- four authored freezer-aisle blockers that create side routes while leaving a readable central service lane,
- two cold-chain breaker circuits distributed across opposite freezer routes,
- a project-owned rear `Cold-Chain Compressor Reset` that appears only after both breakers are restored and supplies the final `3/3` power step,
- a three-second telegraphed right-flank response after each breaker repair: Security Price Scanner first, then Cart of Doom, with no third instant enemy on the compressor transition,
- Angry Self-Checkout, Security Price Scanner, Cart of Doom and Possessed Pallet Jack pressure placed off the entry centerline,
- the existing power-gated Night Manager as the current department supervisor rather than inventing an unvalidated new boss,
- a deterministic management-response anchor after full power,
- a full-power recovery cache before the supervisor fight,
- four telegraphed environmental Overtime hazard anchors kept away from the entry/clock-out approach,
- paired project-owned `FROZEN FOODS` signs, a generated compressor-control pickup, safe restock/cone clutter, slow-failing lights and optional Emergency Break Snacks,
- three department-local Corporate Compliance Memos as an optional exploration route,
- a map-local initializer that clears only memo progress carried from the previous department and then destroys itself so normal save/restore inside MAP03 preserves newly collected memos,
- an original deterministic department track, **Frozen Foods — Compressor Choir**,
- a post-clear `CLOCK OUT` guide and the existing physical front completion rule.

The Frozen Foods objective sequence is now deliberately more department-specific without adding a
random movement gimmick: restore the left/right cold-chain breakers, cross to the rear service position,
perform the compressor reset, use the full-power recovery option if needed, survive the Night Manager
plus authored response pressure, then return to the entry and clock out. The compressor control grants
the same authoritative final power token that hardened cache/boss/wave systems already use, so the new
work task changes route language without forking core progression state.

The first two breaker repairs trigger a readable side-lane answer only after a three-second warning.
The final compressor action deliberately does not spawn another instant side enemy; full power instead
hands pressure to the Night Manager and existing management-response sequence. Overtime side-lane
electrical arcs still turn a long shift into a routing hazard, but their telegraphs and placement keep
the central completion route readable.

This is playable vertical-slice content, not a claim that Frozen Foods is a polished final campaign
level. Future passes can add refrigeration-specific mechanics only after the current route survives
real gameplay validation; slippery movement or freezer-door traps must never become random punishment.

Remaining Frozen Foods polish:
- target-machine balance/readability playtesting across all three difficulty modes,
- stronger cold-storage-specific secrets and encounter variation without obscuring the two breaker routes or compressor task,
- refrigeration/frost interactions only if they remain readable and deterministic,
- final lighting/geometry polish after the objective route is validated in play.

## Later departments

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
