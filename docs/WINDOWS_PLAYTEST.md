# Target-Windows Playtest & Demo Sign-off Evidence

The public demo gate requires a real interactive Windows session. CI parser checks and the automated two-process save/load test are important, but they cannot replace hands-on confirmation of gameplay feel, physical controller behavior, real-hardware performance, balance and final presentation.

## One-click helper

From a source checkout or supported release-candidate layout, run:

```text
PLAYTEST-WINDOWS.bat
```

The helper uses `tools/windows_playtest_assistant.ps1`. It deliberately does **not** publish a release, edit `ROADMAP.md`, or raise any progress percentage.

Before gameplay it:

1. verifies the release-candidate package when `package-manifest.json` is present,
2. prepares the pinned legal runtime through the normal official-source bootstrap,
3. builds and smoke-tests the PK3 only when a source checkout has no current build,
4. creates an isolated GZDoom config so the sign-off session does not overwrite a player's normal settings,
5. records exact SHA-256 hashes for the game PK3, GZDoom executable and Freedoom WAD,
6. records source branch/commit when available, pinned runtime metadata and a best-effort Windows hardware/controller snapshot.

The helper launches two manual GZDoom sessions. The first starts `MAP01 — Closing Time`; make a normal in-game save before exiting. The second launch is intentionally separate so the tester can load that save after a full process exit and confirm the real manual save/quit/load path.

## Required manual gates

A named sign-off report is `PASS` only when **all** of these are explicitly confirmed:

- complete Closing Time from shift start through the physical clock-out trigger,
- create a normal save, fully quit GZDoom, relaunch and load/continue successfully,
- confirm real-controller movement, aiming, actions and signature-weapon haptics,
- confirm **Closing Crew** balance is readable and finishable,
- confirm **Graveyard Shift** feels like the intended baseline,
- confirm **Corporate Hell** is demanding but fair without progression blockers or unreadable pressure spikes,
- confirm real Windows hardware remains responsive through Overtime, boss waves and the post-boss return leg,
- confirm no remaining gameplay/presentation issue makes Closing Time unrepresentative of the intended demo quality.

Use `S / not tested` rather than guessing when a gate was not actually exercised. A failed or untested gate keeps the report `INCOMPLETE`.

## Evidence output

Each run creates a timestamped directory under `playtest-evidence/` unless another evidence root is supplied. The directory contains:

- `evidence.json` — machine-readable source/runtime/file/hardware/gate record,
- `evidence.md` — human-readable sign-off report,
- `gzdoom-playtest.ini` — isolated session config,
- `gzdoom-playtest.log` — engine log when GZDoom creates it.

The evidence report always states that it does **not** authorize a public release. Release notes, the final legal-content packaging decision and GitHub Release publication remain separate repository gates.

## Automation / CI validation

For non-interactive validation:

```powershell
.\tools\windows_playtest_assistant.ps1 -DryRun
```

`-DryRun` validates the helper's static prerequisites and pinned runtime records without downloading runtime files, launching GZDoom, prompting for manual results or claiming sign-off.

`-NoLaunch` prepares real runtime/package evidence and emits an `INCOMPLETE` report with every manual gate marked `NOT_TESTED`; it exists for diagnostics, not as a substitute for gameplay.

## Release policy

A green CI run means the code/package contracts passed. A `PASS` playtest evidence report means only the named **Closing Time target-Windows interactive demo sign-off** scope passed. Neither state alone authorizes a public demo. The repository release rule in `ROADMAP.md` remains authoritative.

CHECKOUT OF HELL — by Swir
