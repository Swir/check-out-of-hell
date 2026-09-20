from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "closing-time-signoff-kit.yml"
text = WORKFLOW.read_text(encoding="utf-8")

exact_head = "github.event.pull_request.head.sha || github.sha"
if text.count(exact_head) < 2:
    raise SystemExit(
        "Closing Time sign-off workflow must checkout the exact PR head SHA in both jobs; "
        "the synthetic pull-request merge ref is not valid exact-candidate evidence."
    )

if "refs/pull/" in text:
    raise SystemExit("Closing Time sign-off workflow must not pin a synthetic refs/pull merge ref")

if "python tools/test_signoff_exact_head_workflow.py" not in text:
    raise SystemExit("Closing Time sign-off workflow must run its exact-head regression contract")

print("Closing Time sign-off exact-head workflow contract: PASS")
