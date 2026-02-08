#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import requests

DEFAULT_BASE_URL = "http://localhost:8765"
DEFAULT_TIMEOUT = 10

SKIP_COMMANDS = {
    "EXIT",
    "DESTROY",
}

DIRECT_COMMANDS = {
    "HELP": "HELP",
    "STATUS": "STATUS",
    "WIZARD": "WIZARD status",
    "OK": "OK LOCAL",
}


def _auth_headers() -> Dict[str, str]:
    token = os.getenv("WIZARD_ADMIN_TOKEN", "").strip()
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _fetch_allowlist(base_url: str) -> List[str]:
    url = f"{base_url.rstrip('/')}/api/ucode/allowlist"
    resp = requests.get(url, headers=_auth_headers(), timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()
    allowlist = payload.get("allowlist") or []
    return sorted({str(item).upper() for item in allowlist if isinstance(item, str)})


def _probe_command(cmd: str) -> str:
    if cmd in DIRECT_COMMANDS:
        return DIRECT_COMMANDS[cmd]
    return f"{cmd} --help"


def _dispatch(base_url: str, command: str) -> Tuple[int, Dict[str, object]]:
    url = f"{base_url.rstrip('/')}/api/ucode/dispatch"
    payload = {"command": command}
    resp = requests.post(url, headers=_auth_headers(), json=payload, timeout=DEFAULT_TIMEOUT)
    try:
        data = resp.json()
    except ValueError:
        data = {"raw": resp.text}
    return resp.status_code, data


def _render_result(status_code: int, data: Dict[str, object]) -> str:
    if status_code >= 400:
        return f"http_{status_code}"
    result = data.get("result") if isinstance(data, dict) else None
    if isinstance(result, dict):
        status = result.get("status")
        if isinstance(status, str):
            return status.lower()
    status = data.get("status") if isinstance(data, dict) else None
    if isinstance(status, str):
        return status.lower()
    return "ok"


def _write_report(report_dir: Path, summary: Dict[str, object]) -> Tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = report_dir / f"ucode-cycle-{ts}.json"
    md_path = report_dir / f"ucode-cycle-{ts}.md"

    json_path.write_text(json.dumps(summary, indent=2))

    lines = []
    lines.append("# uCODE Command Cycle Report")
    lines.append("")
    lines.append(f"Generated: {summary['timestamp']}")
    lines.append(f"Base URL: {summary['base_url']}")
    lines.append(f"Total commands: {summary['counts']['total']}")
    lines.append(f"Succeeded: {summary['counts']['ok']}")
    lines.append(f"Errored: {summary['counts']['error']}")
    lines.append(f"Skipped: {summary['counts']['skipped']}")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    for entry in summary["results"]:
        status = entry["status"]
        cmd = entry["command"]
        probe = entry["probe"]
        detail = entry.get("detail", "")
        suffix = f" ({detail})" if detail else ""
        lines.append(f"- {status}: {cmd} -> {probe}{suffix}")
    lines.append("")

    md_path.write_text("\n".join(lines))
    return json_path, md_path


def main() -> int:
    base_url = os.getenv("WIZARD_BASE_URL", DEFAULT_BASE_URL)
    report_dir = Path(os.getenv("UDOS_MEMORY", "memory")) / "reports"

    try:
        allowlist = _fetch_allowlist(base_url)
    except Exception as exc:
        print(f"Failed to fetch allowlist from {base_url}: {exc}")
        return 2

    results = []
    counts = {"total": 0, "ok": 0, "error": 0, "skipped": 0}

    for cmd in allowlist:
        counts["total"] += 1
        if cmd in SKIP_COMMANDS:
            counts["skipped"] += 1
            results.append({"command": cmd, "probe": "(skipped)", "status": "skipped"})
            continue

        probe = _probe_command(cmd)
        try:
            status_code, data = _dispatch(base_url, probe)
            status = _render_result(status_code, data)
            if status == "ok":
                counts["ok"] += 1
            else:
                counts["error"] += 1
        except Exception as exc:
            status = "error"
            data = {"error": str(exc)}
            counts["error"] += 1

        detail = None
        if isinstance(data, dict):
            detail = data.get("detail") or data.get("error")

        results.append({
            "command": cmd,
            "probe": probe,
            "status": status,
            "http_status": status_code if "status_code" in locals() else None,
            "detail": detail,
            "response": data,
        })

    summary = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "base_url": base_url,
        "counts": counts,
        "results": results,
    }

    json_path, md_path = _write_report(report_dir, summary)
    print(f"Wrote report: {md_path}")
    print(f"Wrote data: {json_path}")
    return 0 if counts["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
