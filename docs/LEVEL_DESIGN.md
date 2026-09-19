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
- one full-power compressor-surge anchor on the right service flank that activates only once Overtime is live, waits 18 seconds before its first burst, telegraphs for two seconds and repeats at deterministic `34 / 26 / 20` second spacing as pressure rises,
- one optional opposite-side `Compressor Surge Isolation` control that suppresses only future refrigeration bursts while hostile Overtime and management remain active,
- paired project-owned `FROZEN FOODS` signs, generated compressor-reset/isolation/burst sprites, safe restock/cone clutter, slow-failing lights and optional Emergency Break Snacks,
- three department-local Corporate Compliance Memos as an optional exploration route,
- a map-local initializer that clears only memo progress carried from the previous department and then destroys itself so normal save/restore inside MAP03 preserves newly collected memos,
- a save-aware surge-state handler that clears isolation only on fresh transitions so a saved safety choice remains stable,
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
hands pressure to the Night Manager and existing management-response sequence. If Overtime is already
active, the powered compressor can begin a separate right-flank refrigeration surge only after an
18-second grace period. Every burst uses the same visible/audio warning language for two full seconds,
and the authored spacing tightens with Overtime stage rather than randomizing the player's safe route.

The opposite-side isolation station is a deliberate optional work task rather than a combat-off switch.
Taking it retires future compressor bursts only. Ambient Overtime enemies, standard electrical hazard
anchors, management waves and the Night Manager remain active. Supervisor clearance also cancels any
armed compressor burst so the post-boss return remains readable. This creates a real workplace choice:
spend movement/time on safety or accept a predictable side-lane hazard while fighting management.

This is playable vertical-slice content, not a claim that Frozen Foods is a polished final campaign
level. Future passes should deepen secrets and cold-storage encounter variety only after the current
route survives real gameplay validation; additional refrigeration gimmicks must never become random
punishment or obscure the central service lane.

Remaining Frozen Foods polish:
- target-machine balance/readability playtesting across all three difficulty modes, including surge spacing and isolation-station placement,
- stronger cold-storage-specific secrets and encounter variation without obscuring the two breaker routes or compressor task,
- final lighting/geometry polish after the objective route and refrigeration pressure survive real play.

## MAP04 — Electronics
Purpose: first playable showroom department with alternating display-wall sightlines, a physical network-recovery task and readable powered-hardware hazards.

Current prototype includes:
- four alternating solid display-wall rows that break long sightlines while preserving a clean central service lane,
- two opposite-side UPS/breaker repairs,
- a project-owned rear `Store Network Reboot` that appears only after both repairs and supplies the final authoritative `3/3` power step,
- a three-second telegraphed side response after each repair: Security Price Scanner first, then Angry Self-Checkout,
- initial Scanner, Self-Checkout, Cart and Pallet Jack pressure placed off the central entry/exit lane,
- a power-gated Night Manager plus the shared deterministic management-response anchor,
- a full-power recovery cache and three optional Corporate Compliance Memos,
- three standard outer-lane Overtime electrical hazard anchors plus one department-specific right-side demo-wall surge,
- a 16-second grace period before the first display surge, two-second warning before every burst and deterministic `32 / 24 / 18` second spacing as Overtime pressure rises,
- one optional opposite-side `Demo Wall Kill Switch` that suppresses only future display surges while hostile Overtime and management remain active,
- paired project-owned Electronics signs, generated network-reboot/kill-switch/surge sprites, safe clutter, slow-failing fixtures and optional Emergency Break Snacks,
- a one-shot entry initializer that clears carried memo/kill-switch state and then destroys itself so saves made after entry preserve local progress,
- the original deterministic **Electronics — Dead Pixel Choir** soundtrack,
- the existing post-clear non-blocking `CLOCK OUT` guide and physical front completion rule.

Electronics deliberately makes the useful workplace task the last power step rather than a cosmetic prop.
The player restores two display/UPS circuits, crosses to the rear service position, physically performs the
Store Network Reboot and only then reaches full power. That pickup grants the same `CheckoutFuse` token
consumed by the hardened full-power cache, supervisor and clock-out systems, avoiding a parallel progression
ledger. The final reboot itself does not spawn a third instant side-lane enemy; management becomes the next
clear pressure beat.

Once full power overlaps Overtime, one outer demo wall can begin faulting. Every burst is announced by the
same project-owned warning language for two seconds, and the first fault cannot occur until a 16-second grace
window has passed. The optional kill switch sits on the opposite side of the floor so choosing safety costs
movement without becoming mandatory. Taking it removes only this Electronics-specific fault source; ambient
Overtime enemies, shared electrical anchors and management continue normally.

This is playable development content, not a polished final campaign level. Future work should deepen showroom
secrets and diversify hardware encounters only after real play confirms that the alternating display walls
stay readable during Overtime and the Night Manager sequence.

Remaining Electronics polish:
- target-machine balance/readability playtesting across all three difficulty modes,
- stronger showroom secrets and useful joke interactions without hiding mandatory power work,
- final lighting/geometry and encounter polish after the current route survives real play.

## MAP05 — Customer Service
Purpose: a tighter complaint-desk department built around serpentine queue sightlines, a real refund-authorization task and escalating customer-pressure jokes that remain readable combat mechanics.

Current prototype includes:
- a long serpentine queue that shapes movement without blocking the central return lane,
- two mandatory service-desk circuits on opposite queue routes,
- a physical rear `Refund Authorization Terminal` that appears after both circuits are restored,
- a save-safe twelve-second Corporate verification hold instead of an instant third power token,
- an authored outer-queue audit sequence: Angry Self-Checkout at 2 seconds, warnings at 5 and 9 seconds, Security Price Scanner at 7 seconds and the Returns Policy Enforcer at 10 seconds,
- the final authoritative `CheckoutFuse 3/3` only at 12 seconds, keeping the shared Night Manager/full-power/clock-out gates authoritative,
- the **Returns Policy Enforcer** miniboss with 220 health, project-owned Self-Checkout presentation and a readable three-way Corporate Red Tape volley,
- a complaint-queue Overtime layer that starts only after a desk circuit is live, waits 20 seconds, warns for two seconds and then calls stage-scaled extra customers at deterministic `38 / 30 / 22` second spacing,
- an eight-second complaint-queue recovery window after the refund audit so the department-specific pressure systems do not stack unfairly,
- an optional opposite-side `Take-A-Number Queue Reset` that suppresses only future complaint-queue calls while standard Overtime and management pressure remain active,
- three optional Corporate Compliance Memos, an optional stash and the existing shared recovery/clock-out systems,
- the original deterministic **Customer Service — Please Hold Forever** soundtrack.

The refund terminal turns a workplace joke into a real objective without forking progression state. The
player restores the two service circuits, crosses to the rear desk and deliberately starts the twelve-second
audit. The first two responses are familiar retail threats, but the final 10-second answer is the
Customer Service-specific Returns Policy Enforcer rather than another Cart of Doom. Its three-way red-tape
fan raises pressure while reusing only project-owned presentation; it never owns a fuse, supervisor token or
separate completion flag. Surviving until 12 seconds grants the same final `CheckoutFuse` consumed by the
shared full-power and Night Manager logic.

Customer Service's extra Overtime layer is deliberately separate from the fixed refund audit. Once a desk
circuit is live and Overtime begins, one authored outer queue lane can call an additional hostile customer
after a 20-second grace period and two-second warning. The response escalates from Angry Self-Checkout to
Security Price Scanner to Cart of Doom as Overtime deepens. While the audit is active the complaint caller
pauses, then gives the player eight seconds to recover before it can resume. Taking the optional Queue Reset
retires only this department-specific caller; it does not disable global Overtime, standard floor hazards,
management waves or the Night Manager.

This is playable development content, not a polished final campaign level. Future work should strengthen
Customer Service-specific visual dressing, secrets and encounter variety only after target-machine playtests
confirm that the queue remains readable during the refund hold, complaint calls and Night Manager pressure.

Remaining Customer Service polish:
- target-machine balance/readability playtesting across all three difficulty modes, especially the 10-second Enforcer handoff and complaint-queue spacing,
- stronger returns-counter/customer-service presentation without replacing project-owned combat assets with proprietary material,
- more useful joke interactions and secrets that do not hide the two service circuits or refund terminal,
- final lighting/geometry and encounter polish after the current route survives real play.

## Later departments

### Management Floor
The campaign's corporate nightmare: cleaner geometry, increasingly absurd executive hazards,
and the final route toward clocking out at 06:00.

## Design rule
Every room should have at least one gameplay joke that still works as a useful combat mechanic.
Humor must not replace readability, and progression gates must be visually understandable without
forcing the player to read long instructions during combat.