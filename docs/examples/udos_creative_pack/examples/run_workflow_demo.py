from __future__ import annotations

from pathlib import Path
from core.creative.phase_engine import PhaseEngine
from examples.workflow_spec_example import build_demo_workflow


def main():
    # Demo vault in local folder (for uDOS, point this to your real vault root)
    vault_root = Path("demo_vault")
    prompt_root = Path("core/creative")

    engine = PhaseEngine(vault_root=vault_root, prompt_root=prompt_root)
    wf = build_demo_workflow()

    print(f"Running workflow: {wf.workflow_id}")
    for phase in wf.phases:
        line = engine.run_with_escalation(wf, phase, start_tier="tier1_local")
        print(" -", line)

    print("Done. Artifacts written under:", vault_root / "workflows" / wf.workflow_id)


if __name__ == "__main__":
    main()
