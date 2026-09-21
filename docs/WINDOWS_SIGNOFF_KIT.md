# Closing Time Windows sign-off kit

The `checkout-of-hell-closing-time-windows-signoff-kit` CI artifact is the lowest-friction way to perform the remaining **real target-Windows** Closing Time polish gate. It is a QA artifact, not a public demo.

## Why the kit exists

The ordinary developer harness remains valid from a clean Git checkout, but the polish gate should not require a human tester to install Git/Python, rebuild the candidate, or hunt for GZDoom/Freedoom. The kit therefore carries the exact CI-built non-public Windows RC plus a small candidate manifest that binds its SHA-256 to the full source commit and branch recorded inside `package-manifest.json`.

The embedded player package still follows the normal distribution policy: verified Freedoom content is bundled legally and missing GZDoom is obtained only from the pinned official upstream release. Network or integrity failures stop the run; there is no unofficial-mirror fallback.

## One-click flow

1. Download the `checkout-of-hell-closing-time-windows-signoff-kit` artifact for the exact candidate commit.
2. Extract the whole ZIP to a writable Windows folder.
3. Connect the physical controller used for the test.
4. Double-click `RUN-SIGNOFF.bat`.
5. Complete all three guided `MAP01 — Closing Time` passes and answer only from what actually happened.
6. Complete the explicit polish review for environment/art consistency, objective/route readability, lighting/atmosphere, and clutter/visual hierarchy; a generic final yes/no alone is not sufficient evidence for canonical polish closure.
7. Stay in the same one-click flow while `RUN-SIGNOFF.bat` locks/verifies the real Graveyard Shift manual-save artifact and then automatically runs the independent consistency verifier. Final success is reported only if gameplay/hardware, explicit polish, manual-save witness and exact-candidate evidence verification all pass.

`VERIFY-EVIDENCE.bat` remains available to re-run the independent verification later without replaying the human judgments. Its wrapper re-checks the same `manual-save-witness.sha256` first.

The tester never needs to search for a runtime, WAD, Python installation or other dependency manually. The verifier reuses system Python when available or bootstraps the pinned portable Python build from `python.org`.

## Candidate binding

`SIGNOFF-CANDIDATE.json` contains:

- the full 40-character source commit;
- the source branch/ref;
- the clean-source requirement;
- the exact embedded RC SHA-256;
- `public_release: false`.

Before any manual prompt, `tools/windows_signoff_kit.ps1` verifies the outer RC hash, extracts it, checks the RC `package-manifest.json` source provenance, runs the package integrity verifier, prepares the pinned official runtime, and completes the real save -> process exit -> load round-trip against that exact payload.

After the base gameplay/hardware pass, `tools/closing_time_polish_review.ps1` records four separate manual judgments into that same evidence record: `environment_art_consistent`, `objective_route_readable`, `lighting_atmosphere_acceptable`, and `clutter_visual_hierarchy_clean`. A failed answer changes the evidence status away from `PASS`.

`RUN-SIGNOFF.bat` then invokes `tools/verify_signoff_kit.ps1`. Before delegating to the Python consistency verifier, that helper requires a plausible human-created Graveyard Shift save under `manual-saves`: it must be a non-autosave `.zds` file of at least 1 KiB. On first canonical verification it writes the selected save path and SHA-256 to `manual-save-witness.sha256`; later verification rejects a missing, replaced or hash-changed save. This protects the file artifact but does not replace the tester's explicit `save_quit_load` judgment.

The helper then feeds the newest evidence directory and exact candidate commit into `tools/verify_windows_signoff_evidence.py`. A forged/stale PASS, a missing explicit polish field, a failed polish field, a missing/changed manual-save witness, or evidence from a different commit is rejected before the one-click runner reports final success.

## Human gates remain human

Hosted CI only builds/tests the kit and parses its PowerShell. It does **not** pretend to be the physical target machine. Canonical Closing Time polish closure still requires all three difficulty runs, manual Graveyard Shift save/quit/load, per-difficulty combat readability and balance confirmation, physical-controller core actions and haptics, real-hardware Overtime/Night Manager sanity, explicit environment/art consistency, objective/route readability, lighting/atmosphere, clutter/visual hierarchy, and `final_polish_signoff = true`.

No script in the kit creates a GitHub Release or authorizes a public demo. Remaining `ROADMAP.md` release gates continue to apply.
