from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from fastapi import HTTPException


class ContributionService:
    STATUSES = ("pending", "approved", "rejected")

    def __init__(self, vault_root: Path):
        self.root = vault_root / "contributions"
        self.root.mkdir(parents=True, exist_ok=True)
        self.status_dirs = {
            status: (self.root / status) for status in self.STATUSES
        }
        for directory in self.status_dirs.values():
            directory.mkdir(parents=True, exist_ok=True)

    def list(self, status: Optional[str] = None) -> List[Dict[str, Optional[str]]]:
        statuses = [status] if status else list(self.STATUSES)
        entries: List[Dict[str, Optional[str]]] = []
        for st in statuses:
            if st not in self.status_dirs:
                continue
            for item in sorted(self.status_dirs[st].iterdir()):
                if not item.exists():
                    continue
                manifest = self._load_manifest(item)
                entries.append(
                    {
                        "id": item.name,
                        "status": st,
                        "path": item.relative_to(self.root).as_posix(),
                        "manifest": manifest,
                    }
                )
        return entries

    def find(self, contribution_id: str) -> Tuple[Optional[Path], Optional[str]]:
        for status, directory in self.status_dirs.items():
            candidate = directory / contribution_id
            if candidate.exists():
                return candidate, status
        return None, None

    def get_entry(self, contribution_id: str) -> Dict[str, Optional[str]]:
        entry, status = self.find(contribution_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Contribution not found")
        manifest = self._load_manifest(entry)
        return {
            "id": contribution_id,
            "status": status,
            "manifest": manifest,
            "path": entry.relative_to(self.root).as_posix(),
        }

    def submit(self, payload: Dict[str, Optional[object]]) -> Dict[str, Optional[str]]:
        contribution_id = (
            str(payload.get("id")) if payload.get("id") else f"contrib-{uuid.uuid4().hex[:8]}"
        )
        target = self.status_dirs["pending"] / contribution_id
        if target.exists():
            raise HTTPException(status_code=409, detail="Contribution already exists")
        target.mkdir(parents=True, exist_ok=False)
        manifest = self._build_manifest(contribution_id, payload)
        self._write_manifest(target, manifest)
        if patch := payload.get("patch"):
            self._write_patch(target, str(patch))
        if bundle := payload.get("bundle"):
            self._write_bundle(target, bundle)
        return {
            "id": contribution_id,
            "status": "pending",
            "manifest": manifest,
            "path": target.relative_to(self.root).as_posix(),
        }

    def update_status(
        self,
        contribution_id: str,
        status: str,
        reviewer: Optional[str],
        note: Optional[str],
    ) -> Dict[str, Optional[str]]:
        if status not in self.status_dirs:
            raise HTTPException(status_code=400, detail="Invalid status")
        current, current_status = self.find(contribution_id)
        if not current:
            raise HTTPException(status_code=404, detail="Contribution not found")
        destination = self.status_dirs[status] / contribution_id
        if destination.exists():
            raise HTTPException(
                status_code=409, detail="Contribution already marked with this status"
            )
        shutil.move(str(current), str(destination))
        manifest = self._load_manifest(destination)
        manifest["status"] = status
        manifest["reviewer"] = reviewer
        manifest["status_history"] = manifest.get("status_history", [])
        manifest["status_history"].append(
            {
                "status": status,
                "reviewer": reviewer,
                "note": note,
                "ts": datetime.utcnow().isoformat() + "Z",
            }
        )
        manifest["updated_at"] = datetime.utcnow().isoformat() + "Z"
        self._write_manifest(destination, manifest)
        return {
            "id": contribution_id,
            "status": status,
            "manifest": manifest,
            "path": destination.relative_to(self.root).as_posix(),
        }

    def _load_manifest(self, entry: Path) -> Dict[str, Optional[object]]:
        manifest_file = self._ensure_manifest_file(entry)
        if not manifest_file:
            return {"id": entry.name}
        text = manifest_file.read_text()
        try:
            if manifest_file.suffix.lower() in (".yml", ".yaml"):
                data = yaml.safe_load(text)
            else:
                data = json.loads(text)
        except (json.JSONDecodeError, yaml.YAMLError):
            return {"id": entry.name}
        return data if isinstance(data, dict) else {"id": entry.name}

    def _ensure_manifest_file(self, entry: Path) -> Optional[Path]:
        if entry.is_file():
            return entry if entry.name.startswith("manifest") else None
        for name in ("manifest.json", "manifest.yaml", "manifest.yml"):
            candidate = entry / name
            if candidate.exists():
                return candidate
        return None

    def _write_manifest(self, entry: Path, manifest: Dict[str, Optional[object]]) -> None:
        target = entry / "manifest.json"
        target.write_text(json.dumps(manifest, indent=2))

    def _write_patch(self, entry: Path, patch: str) -> None:
        (entry / "patch.diff").write_text(patch)

    def _write_bundle(self, entry: Path, bundle: object) -> None:
        (entry / "bundle.json").write_text(json.dumps(bundle, indent=2))

    def _build_manifest(self, contribution_id: str, payload: Dict[str, Optional[object]]) -> Dict[str, Optional[object]]:
        now = datetime.utcnow().isoformat() + "Z"
        manifest: Dict[str, Optional[object]] = {
            "id": contribution_id,
            "status": "pending",
            "created_at": now,
            "updated_at": now,
        }
        if mission := payload.get("mission_id"):
            manifest["mission_id"] = mission
        if notes := payload.get("notes"):
            manifest["notes"] = notes
        if artifact := payload.get("artifact"):
            manifest["artifact"] = artifact
        manifest["status_history"] = [
            {"status": "pending", "reviewer": None, "note": "submission", "ts": now}
        ]
        return manifest
