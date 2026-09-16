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
sprites, interaction/PA cues, the Emergency Mop first-person animation set and the Night
Manager prototype animation/attack presentation. The Night Manager also uses an original
Manager Memo projectile instead of inheriting a commercial/IWAD projectile visual.

Generated sprite PNGs include ZDoom-compatible `grAb` offsets so their placement is
explicit and reproducible. The generator uses only Python's standard library and therefore
does not add a new runtime or build dependency.

Combat actors and weapon view sprites that have not yet received original art may still
reference compatible IWAD-provided placeholders at runtime. Those placeholder assets are
never copied into this repository or release package. Current remaining examples include
the Receipt Ripper, Price-Gun SMG, Turbo Can Launcher and several non-boss enemy actors.

## Final strategy

Replace every remaining placeholder visual/audio dependency with original project assets
before calling the game standalone. Original generated prototype assets may be replaced by
hand-authored production art later, but their source must remain traceable and legally safe.
