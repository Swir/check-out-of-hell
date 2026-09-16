# Managed runtime directory

Do not commit downloaded third-party runtime binaries here.

Normal users should simply run `PLAY.bat`. The bootstrap will automatically populate this directory from the official upstream sources pinned in `runtime-lock.json`.

Expected generated files include:

```text
external/
  gzdoom/
    gzdoom.exe
    ...
  freedoom2.wad
  runtime-manifest.json
```

No manual dependency search is required.
