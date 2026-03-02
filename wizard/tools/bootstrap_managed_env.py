from __future__ import annotations

import os

from wizard.services.store import get_wizard_store


def main() -> int:
    store = get_wizard_store()
    store.update_scheduler_settings(
        {
            "max_tasks_per_tick": 4,
            "tick_seconds": 60,
            "allow_network": True,
        }
    )
    subjects = [
        (os.environ.get("UDOS_BOOTSTRAP_ADMIN_SUBJECT") or "").strip(),
        (os.environ.get("UDOS_BOOTSTRAP_OPERATOR_SUBJECT") or "").strip(),
    ]
    roles = ["admin", "operator"]
    for subject, role in zip(subjects, roles):
        if not subject:
            continue
        store.get_operator_profile(subject)
        store.set_operator_role(subject, role)
        print(f"seeded {role} subject {subject}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
