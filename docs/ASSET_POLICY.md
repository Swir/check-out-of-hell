# Asset Policy

## Allowed in the repository

- Original project code and original assets.
- Deterministically generated original prototype art/audio produced by repository tooling.
- Assets explicitly licensed for redistribution under compatible terms.
- Freedoom assets when their BSD 3-Clause notice/credit is preserved.
- Temporary references to runtime-provided actor/sprite names for development,
  provided the proprietary assets themselves are not redistributed.

## Not allowed

- Doom IWAD data.
- Commercial Doom sprites/textures/music/sounds.
- Star Wars characters, logos, models, music, voice clips or textures.
- Ripped assets from any commercial game.

## Prototype strategy

The project generates an original retail atmosphere/combat pack during the build:
store walls, shelf fronts, Staff Only surfaces, floor/ceiling materials, objective pickup
sprites, interaction/PA cues and an expanding set of project-owned combat presentation.

Current project-owned signature combat presentation includes:
- Emergency Mop first-person animation + swing cue,
- Receipt Ripper pickup + five-frame first-person animation + fire/cycle cues,
- Price-Gun SMG pickup + five-frame automatic weapon animation + barcode-label impact puffs and cues,
- Turbo Can Launcher pickup + five-frame launcher animation + original can projectile/explosion and cues,
- Angry Self-Checkout animation set + hostile receipt projectile + combat cues,
- Security Price Scanner turret animation + original scan-beam projectile + combat cues,
- Night Manager animation set + Manager Memo projectile + boss cues.

Generated sprite PNGs include ZDoom-compatible `grAb` offsets so their placement is
explicit and reproducible. The original atmosphere generator and the combat-asset extension
use only Python's standard library and therefore do not add a new runtime or build dependency.

Combat actors that have not yet received original art may still reference compatible
IWAD-provided placeholders at runtime. Those placeholder assets are never copied into this
repository or release package. Current remaining visible placeholder examples are Cart of
Doom, Possessed Pallet Jack and Regional Manager prototype.

## Final strategy

Replace every remaining placeholder visual/audio dependency with original project assets
before calling the game standalone. Original generated prototype assets may be replaced by
hand-authored production art later, but their source must remain traceable and legally safe.
