# Target Windows demo sign-off

The public demo gate requires evidence from a real interactive Windows machine. Hosted CI can validate packaging, parsing and the real two-process save/load behavior on the pinned engine, but it cannot replace human judgment about combat readability, balance, controller feel or real-hardware performance.

## Recommended one-click candidate kit

For the Closing Time final-polish candidate, use the CI artifact named:

```text
checkout-of-hell-closing-time-windows-signoff-kit
```

Extract the artifact ZIP, then extract `CHECKOUT-OF-HELL-Windows-Signoff-Kit.zip` and double-click:

```text
RUN-SIGNOFF.bat
```

The kit is bound to the exact clean CI source snapshot and embedded RC SHA-256 through `SIGNOFF-CANDIDATE.json`. It means the target-Windows tester does **not** need to clone the repository, install Git/Python, rebuild the game or search for GZDoom/Freedoom manually. After a real PASS, double-click `VERIFY-EVIDENCE.bat`; it independently verifies the newest evidence directory against the same candidate commit. See `docs/WINDOWS_SIGNOFF_KIT.md` for the artifact contract.

The kit does not publish anything and is not a public demo.

## Developer checkout entry point

A clean Git checkout of the exact candidate commit remains supported. On the Windows machine, double-click:

```text
WINDOWS-DEMO-SIGNOFF.bat
```

Equivalent PowerShell command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows_demo_signoff.ps1
```

The developer harness creates a fresh evidence directory under:

```text
dist\windows-demo-signoff\<UTC timestamp>\
```

The one-click CI kit stores the same evidence schema below its local `evidence\<UTC timestamp>\` directory.

## What is automatic

Before asking for any gameplay judgment, either flow:

1. identifies the exact non-public `CHECKOUT-OF-HELL-Windows-Portable-rc.zip`,
2. records and verifies the outer package SHA-256,
3. extracts that ZIP into the evidence directory,
4. runs the package's own `verify_player_package.ps1` manifest/integrity check,
5. prepares the pinned GZDoom runtime through the package's official-source bootstrap while using the bundled verified Freedoom content,
6. runs a real GZDoom save -> process exit -> load round-trip against the **exact extracted player PK3**, bundled Freedoom WAD and prepared GZDoom executable,
7. records the runtime identity plus a privacy-limited hardware summary.

The CI sign-off kit additionally verifies that its `SIGNOFF-CANDIDATE.json`, embedded RC SHA-256 and RC `package-manifest.json` agree on the exact source commit/branch/clean state before any manual play begins.

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

- source branch/commit and verified clean-source provenance,
- RC SHA-256,
- pinned GZDoom/Freedoom identity and local verified runtime hashes where available,
- Windows/CPU/GPU/RAM information,
- controller **friendly names only**,
- automated gate results,
- every manual confirmation.

It intentionally does **not** collect user/account names, machine names, serial numbers, hardware IDs or device IDs. Evidence is not uploaded automatically.

## Independent evidence verification

From a clean developer checkout, completed evidence can still be checked with:

```powershell
python .\tools\verify_windows_signoff_evidence.py .\dist\windows-demo-signoff\<UTC timestamp> --expected-commit <40-character commit>
```

The CI kit's `VERIFY-EVIDENCE.bat` performs the equivalent check against its own exact candidate commit and bootstraps pinned Python from the official `python.org` source when necessary.

The verifier does **not** replay or replace the human gameplay judgment. It independently rejects stale or tampered evidence when the source commit/branch/clean state, required manual and automated gates, extracted package manifest entries, pinned runtime identity and hashes, Freedoom provenance, manual-save presence or save/load completion markers no longer agree.

This verification is local, uploads nothing and does not publish or authorize a demo. A failed consistency check invalidates the evidence until the underlying problem is resolved and a trustworthy sign-off is produced.

## Result semantics

- `PASS` means every automated check and every required manual target-Windows check passed on the exact clean commit-addressable candidate snapshot.
- `FAIL` means at least one required manual or source-verifiability gate failed.
- `FAILED_AUTOMATION` means package/runtime/save-load preparation failed before manual sign-off.
- `INCOMPLETE` means the harness was run in automated-preparation mode, so manual evidence was intentionally not collected.

A `PASS` is **necessary evidence for the interactive Windows gate, not permission to publish by itself**. Before it is used as release-gate evidence, the resulting directory must also pass `verify_windows_signoff_evidence.py` against the exact candidate commit. The current `ROADMAP.md` remains authoritative: legal-content packaging/release-notes/GitHub Release gates must still be completed, and no public demo should be created until the project is genuinely ready.

## Automated-only preparation

Developer-checkout flow:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\windows_demo_signoff.ps1 -PrepareOnly
```

The kit harness also accepts `-PrepareOnly` when invoked directly. Either path intentionally ends with `INCOMPLETE`; it can never be used to claim the human Windows sign-off passed.
