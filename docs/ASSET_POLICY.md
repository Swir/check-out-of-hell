# Asset Policy

## Allowed in the repository

- Original project code and original assets.
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

The prototype PK3 contains code and generated maps only. It is tested by the
developer against a separately obtained compatible IWAD such as Freedoom.

## Final strategy

Replace every placeholder visual/audio dependency with original project assets
before calling the game standalone.
