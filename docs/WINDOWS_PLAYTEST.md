# Target Windows demo sign-off

The public demo gate requires evidence from a real interactive Windows machine. Hosted CI can validate packaging, parsing and the real two-process save/load behavior on the pinned engine, but it cannot replace human judgment about combat readability, balance, controller feel or real-hardware performance.

## One-click developer entry point

Use a **clean Git checkout** of the exact candidate commit on the Windows machine that will perform the sign-off, then double-click:

```text
WINDOWS-DEMO-SIGNOFF.bat
```

Equivalent PowerShell command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows_demo_signoff.ps1
```

The harness does not publish anything. It creates a fresh evidence directory under:

```text
dist\windows-demo-signoff\<UTC timestamp>\
```

## What is automatic

Before asking for any gameplay judgment, the harness:

1. builds the exact non-public `CHECKOUT-OF-HELL-Windows-Portable-rc.zip`,
2. records the outer package SHA-256,
3. extracts that ZIP into the evidence directory,
4. runs the package's own `verify_player_package.ps1` manifest/integrity check,
5. prepares the pinned GZDoom runtime through the package's official-source bootstrap while using the bundled verified Freedoom content,
6. runs a real GZDoom save -> process exit -> load round-trip against the **exact extracted player PK3**, bundled Freedoom WAD and prepared GZDoom executable,
7. records the runtime identity plus a privacy-limited hardware summary.

The automated save/load pass deliberately reuses `tools/gzdoom_save_load_smoke.ps1` with caller-supplied RC paths. It does not rebuild or swap the tested payload after package verification.

## What still requires a person

The harness then guides three real `MAP01 — Closing Time` runs:

- **Closing Crew** — full breaker -> Night Manager -> physical clock-out completion,
- **Graveyard Shift** — create a normal save after objective progress, fully quit GZDoom, relaunch, load that save, confirm restored state and finish the level,
- **Corporate Hell** — full completion on the high-pressure mode.

For each applicable run, answer the prompts only from what actually happened. The final PASS also requires:

- no crash, progression blocker or softlock,
- readable enemies, Overtime warnings and clock-out route,
- acceptable balance for each difficulty's intended role,
- a **physical controller** used successfully for core actions,
- signature-weapon haptics that remain useful rather than disruptive,
- a real-hardware performance sanity check through Overtime and the Night Manager encounter,
- explicit confirmation that Closing Time is polished enough to represent the intended final direction.

The script intentionally does not invent an FPS threshold. A noticeable sustained performance problem is a failed sign-off and should be investigated before release.

## Evidence files

The evidence directory contains:

```text
REPORT.md
 evidence.json
 gzdoom-save-load-smoke.log
 save-load-runtime\...
 manual-saves\...
 playtest.ini
 package\...
```

`evidence.json` is the machine-readable source. `REPORT.md` is a compact human-readable summary. The evidence records:

- source branch/commit and whether the Git tree was clean,
- RC SHA-256,
- pinned GZDoom/Freedoom identity and local verified runtime hashes where available,
- Windows/CPU/GPU/RAM information,
- controller **friendly names only**,
- automated gate results,
- every manual confirmation.

It intentionally does **not** collect user/account names, machine names, serial numbers, hardware IDs or device IDs. Evidence is not uploaded automatically.

## Result semantics

- `PASS` means every automated check and every required manual target-Windows check passed on a clean, commit-addressable source snapshot.
- `FAIL` means at least one required manual or source-verifiability gate failed.
- `FAILED_AUTOMATION` means package/runtime/save-load preparation failed before manual sign-off.
- `INCOMPLETE` means the harness was run with `-PrepareOnly`, so manual evidence was intentionally not collected.

A `PASS` is **necessary evidence for the interactive Windows gate, not permission to publish by itself**. The current `ROADMAP.md` remains authoritative: legal-content packaging/release-notes/GitHub Release gates must still be completed, and no public demo should be created until the project is genuinely ready.

## Automated-only preparation

To verify the exact RC package/runtime/save-load chain without launching manual sessions:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows_demo_signoff.ps1 -PrepareOnly
```

This intentionally ends with `INCOMPLETE`; it can never be used to claim the human Windows sign-off passed.
