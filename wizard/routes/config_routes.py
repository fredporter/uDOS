"""
Configuration Management Routes
================================

Handle reading/writing configuration files locally.
Private configs (API keys, secrets) are only accessible on local machine.
Public repo contains templates only.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse


def create_config_routes(auth_guard=None):
    """Create configuration management routes."""
    router = APIRouter(prefix="/api/v1/config", tags=["config"])

    CONFIG_PATH = Path(__file__).parent.parent / "config"

    # Map config file IDs to actual filenames
    CONFIG_FILES = {
        "ai_keys": "ai_keys.json",
        "github_keys": "github_keys.json",
        "notion_keys": "notion_keys.json",
        "oauth": "oauth_providers.json",
        "slack_keys": "slack_keys.json",
        "wizard": "wizard.json",
    }

    @router.get("/files")
    async def get_config_files():
        """List available config files with their status."""
        files = []

        for file_id, filename in CONFIG_FILES.items():
            file_path = CONFIG_PATH / filename

            # Determine if file exists and is example/template
            if file_path.exists():
                with open(file_path, "r") as f:
                    try:
                        content = json.load(f)
                        files.append(
                            {
                                "id": file_id,
                                "label": filename.replace("_", " ")
                                .replace(".json", "")
                                .title(),
                                "filename": filename,
                                "exists": True,
                                "is_example": filename.endswith(".example.json"),
                                "is_template": filename.endswith(".template.json"),
                            }
                        )
                    except json.JSONDecodeError:
                        files.append(
                            {
                                "id": file_id,
                                "label": filename.replace("_", " ")
                                .replace(".json", "")
                                .title(),
                                "filename": filename,
                                "exists": True,
                                "is_example": False,
                                "is_template": False,
                                "error": "Invalid JSON",
                            }
                        )
            else:
                # Check for .example or .template versions
                example_path = CONFIG_PATH / filename.replace(".json", ".example.json")
                template_path = CONFIG_PATH / filename.replace(
                    ".json", ".template.json"
                )

                if example_path.exists():
                    files.append(
                        {
                            "id": file_id,
                            "label": filename.replace("_", " ")
                            .replace(".json", "")
                            .title(),
                            "filename": filename,
                            "exists": False,
                            "is_example": True,
                            "is_template": False,
                            "actual_file": filename.replace(".json", ".example.json"),
                        }
                    )
                elif template_path.exists():
                    files.append(
                        {
                            "id": file_id,
                            "label": filename.replace("_", " ")
                            .replace(".json", "")
                            .title(),
                            "filename": filename,
                            "exists": False,
                            "is_example": False,
                            "is_template": True,
                            "actual_file": filename.replace(".json", ".template.json"),
                        }
                    )
                else:
                    files.append(
                        {
                            "id": file_id,
                            "label": filename.replace("_", " ")
                            .replace(".json", "")
                            .title(),
                            "filename": filename,
                            "exists": False,
                            "is_example": False,
                            "is_template": False,
                            "actual_file": None,
                        }
                    )

        return {"files": files}

    @router.get("/{file_id}")
    async def get_config(file_id: str):
        """Get configuration file content.

        Only works for actual config files (not examples).
        """
        if file_id not in CONFIG_FILES:
            raise HTTPException(
                status_code=400, detail=f"Unknown config file: {file_id}"
            )

        filename = CONFIG_FILES[file_id]
        file_path = CONFIG_PATH / filename

        # Try actual file first
        if file_path.exists():
            with open(file_path, "r") as f:
                try:
                    content = json.load(f)
                    return {
                        "id": file_id,
                        "filename": filename,
                        "content": content,
                        "is_example": False,
                        "is_template": False,
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500, detail=f"Invalid JSON in {filename}: {str(e)}"
                    )

        # Try example version
        example_path = CONFIG_PATH / filename.replace(".json", ".example.json")
        if example_path.exists():
            with open(example_path, "r") as f:
                try:
                    content = json.load(f)
                    return {
                        "id": file_id,
                        "filename": filename,
                        "content": content,
                        "is_example": True,
                        "is_template": False,
                        "message": "Using example file. Save to create actual config.",
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid JSON in {example_path.name}: {str(e)}",
                    )

        # Try template version
        template_path = CONFIG_PATH / filename.replace(".json", ".template.json")
        if template_path.exists():
            with open(template_path, "r") as f:
                try:
                    content = json.load(f)
                    return {
                        "id": file_id,
                        "filename": filename,
                        "content": content,
                        "is_example": False,
                        "is_template": True,
                        "message": "Using template file. Save to create actual config.",
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid JSON in {template_path.name}: {str(e)}",
                    )

        raise HTTPException(status_code=404, detail=f"Config file not found: {file_id}")

    @router.post("/{file_id}")
    async def save_config(file_id: str, body: Dict[str, Any]):
        """Save configuration file.

        Creates or updates the actual config file (not examples).
        Private files are never distributed in public repo.
        """
        if file_id not in CONFIG_FILES:
            raise HTTPException(
                status_code=400, detail=f"Unknown config file: {file_id}"
            )

        try:
            filename = CONFIG_FILES[file_id]
            file_path = CONFIG_PATH / filename

            # Extract content from request body
            content = body.get("content", {})

            # Validate JSON
            if not isinstance(content, dict):
                raise HTTPException(
                    status_code=400, detail="Config content must be a JSON object"
                )

            # Write file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(content, f, indent=2)

            return {
                "success": True,
                "message": f"Saved {filename}",
                "file": filename,
                "path": str(file_path),
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save config: {str(e)}"
            )

    @router.post("/{file_id}/reset")
    async def reset_config(file_id: str):
        """Reset config file to example/template version."""
        if file_id not in CONFIG_FILES:
            raise HTTPException(
                status_code=400, detail=f"Unknown config file: {file_id}"
            )

        try:
            filename = CONFIG_FILES[file_id]
            file_path = CONFIG_PATH / filename

            # Delete actual config if it exists
            if file_path.exists():
                file_path.unlink()
                return {
                    "success": True,
                    "message": f"Reset {filename} to example/template",
                }
            else:
                raise HTTPException(
                    status_code=404, detail=f"No config file to reset: {filename}"
                )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to reset config: {str(e)}"
            )

    @router.get("/{file_id}/example")
    async def get_example_config(file_id: str):
        """Get example/template version of config file."""
        if file_id not in CONFIG_FILES:
            raise HTTPException(
                status_code=400, detail=f"Unknown config file: {file_id}"
            )

        filename = CONFIG_FILES[file_id]

        # Try example first
        example_path = CONFIG_PATH / filename.replace(".json", ".example.json")
        if example_path.exists():
            with open(example_path, "r") as f:
                try:
                    content = json.load(f)
                    return {
                        "id": file_id,
                        "filename": filename,
                        "example_file": example_path.name,
                        "content": content,
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500, detail=f"Invalid JSON: {str(e)}"
                    )

        # Try template
        template_path = CONFIG_PATH / filename.replace(".json", ".template.json")
        if template_path.exists():
            with open(template_path, "r") as f:
                try:
                    content = json.load(f)
                    return {
                        "id": file_id,
                        "filename": filename,
                        "template_file": template_path.name,
                        "content": content,
                    }
                except json.JSONDecodeError as e:
                    raise HTTPException(
                        status_code=500, detail=f"Invalid JSON: {str(e)}"
                    )

        raise HTTPException(
            status_code=404, detail=f"No example/template found for {filename}"
        )

    return router
