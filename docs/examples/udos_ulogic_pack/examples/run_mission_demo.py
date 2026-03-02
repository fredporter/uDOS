from __future__ import annotations
from pathlib import Path
import shutil
from core.ulogic.engine.runtime import ULogicRuntime
from core.ulogic.engine.contracts import ActorContext

def main():
    project_root = Path("examples/demo_project").resolve()
    vault_root = Path("demo_vault").resolve()
    if vault_root.exists():
        shutil.rmtree(vault_root)
    vault_root.mkdir(parents=True, exist_ok=True)

    rt = ULogicRuntime(project_root=project_root, vault_root=vault_root)
    actor = ActorContext(role="Operator", allow_destructive=False)
    mission = project_root / "missions" / "bootstrap-offline-engine.md"
    result = rt.run_mission_file(mission, actor)
    print(result)
    print("Artifacts:", vault_root)

if __name__ == "__main__":
    main()
