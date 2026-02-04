import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import requests

from spatial_indexer import sync_spatial_index
from task_indexer import TaskIndexer

logging.basicConfig(level=logging.INFO, format="[mission-scheduler] %(message)s")

WIZARD_RENDER_URL = os.getenv("WIZARD_RENDER_URL", "http://wizard-core:8765/api/renderer/render")
WIZARD_API_BASE = os.getenv("WIZARD_API_BASE", "http://wizard-core:8765")
VAULT_ROOT = Path(os.getenv("VAULT_ROOT", "/workspace/vault"))
THEME = os.getenv("THEME", "prose")
CONTRIBUTIONS_DIR = Path(os.getenv("CONTRIBUTIONS_DIR", f"{VAULT_ROOT}/contributions/pending"))
PROCESSED_DIR = CONTRIBUTIONS_DIR.parent / "processed"
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "30"))
RUNS_DIR = VAULT_ROOT / "06_RUNS"
LOGS_DIR = VAULT_ROOT / "07_LOGS"
TASK_INDEXER = TaskIndexer()

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
CONTRIBUTIONS_DIR.mkdir(parents=True, exist_ok=True)
RUNS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def trigger_render(theme: str, mission_id: Optional[str] = None) -> None:
    try:
        response = requests.post(WIZARD_RENDER_URL, json={"theme": theme}, timeout=10)
        response.raise_for_status()
        payload = response.json()
        job_id = payload.get("job_id") or f"job-{int(time.time())}"
        rendered_files = payload.get("rendered", [])
        logging.info("Triggered render job for theme %s (job_id=%s)", theme, job_id)
        task_counts = TASK_INDEXER.index_vault(VAULT_ROOT)
        _record_run(
            job_id,
            theme,
            mission_id or job_id,
            task_counts,
            "completed",
            rendered_files,
        )
        sync_spatial_index(WIZARD_API_BASE)
    except requests.RequestException as exc:
        logging.error("Render trigger failed: %s", exc)


def _record_run(
    job_id: str,
    theme: str,
    mission_id: Optional[str],
    task_stats: Dict[str, int],
    status: str,
    rendered_files: Optional[list] = None,
) -> None:
    mission = mission_id or job_id
    run_dir = RUNS_DIR / f"{mission}"
    run_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "mission_id": mission,
        "job_id": job_id,
        "theme": theme,
        "status": status,
        "task_counts": task_stats,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": datetime.utcnow().isoformat() + "Z",
    }
    if rendered_files:
        report["rendered_files"] = rendered_files
    report_path = run_dir / "report.json"
    run_dir.joinpath("log.txt").write_text(f"[{report['completed_at']}] Render {status}\n")
    task_stats_str = ", ".join(f"{k}={v}" for k, v in task_stats.items())
    rendered_count = len(rendered_files or [])
    LOGS_DIR.joinpath(f"{mission}.log").write_text(
        f"[{report['completed_at']}] {task_stats_str} | rendered_files={rendered_count}\n"
    )
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)


def process_contributions() -> None:
    contributions = sorted(CONTRIBUTIONS_DIR.glob("*.json"))
    if not contributions:
        return
    logging.info("Processing %d contribution(s)", len(contributions))
    for contribution_path in contributions:
        try:
            with open(contribution_path) as fh:
                bundle = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logging.warning("Invalid contribution %s: %s", contribution_path.name, exc)
            contribution_path.unlink(missing_ok=True)
            continue
        mission = bundle.get("mission_id") or bundle.get("artifact")
        logging.info("Contribution %s targets %s", contribution_path.name, mission or "unknown mission")
        trigger_render(THEME, mission)
        target = PROCESSED_DIR / contribution_path.name
        contribution_path.replace(target)


def main() -> None:
    logging.info("Mission scheduler watching %s", CONTRIBUTIONS_DIR)
    while True:
        process_contributions()
        # Periodically refresh exports even without contributions
        trigger_render(THEME)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
