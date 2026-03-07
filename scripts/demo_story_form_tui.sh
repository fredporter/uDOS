#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-.venv}"
export UDOS_STORY_FORM_TUI="${UDOS_STORY_FORM_TUI:-1}"

if [[ -x "./.venv/bin/python" ]]; then
  PYTHON_BIN="./.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "No python interpreter found (expected .venv or python3 on PATH)." >&2
  exit 127
fi

MODE="${1:-run}"
if [[ "$MODE" == "--spec" ]]; then
  MODE="spec"
fi

"$PYTHON_BIN" - <<'PY' "$MODE"
from __future__ import annotations

import json
import sys
from textwrap import dedent

from core.services.story_service import parse_story_document
from core.tui.story_form_handler import get_form_handler

mode = (sys.argv[1] if len(sys.argv) > 1 else "run").strip().lower()

story_markdown = dedent(
    """\
    ---
    title: "TUI Story Form Elements Demo"
    type: story
    version: 1.5.1
    submit_endpoint: "/api/setup/story/submit"
    ---

    # Identity
    This stage demonstrates text + textarea fields.

    ```story
    name: user_username
    label: User name
    type: text
    required: true
    placeholder: Your handle
    ```

    ```story
    name: mission_notes
    label: Mission notes
    type: textarea
    required: false
    placeholder: Optional notes for this binder
    ```

    ---

    # Preferences
    This stage demonstrates selector options and checkboxes.

    ```story
    name: user_role
    label: Role
    type: select
    required: true
    options:
      - Admin
      - User
      - Builder
      - Observer
    ```

    ```story
    name: user_permissions
    label: Permissions
    type: checkbox
    required: true
    options:
      - read
      - write
      - execute
    ```

    ---

    # Time and Place
    This stage demonstrates number/date/time/datetime_approve/location controls.

    ```story
    name: install_moves_limit
    label: Daily move limit
    type: number
    required: true
    min_value: 1
    max_value: 500
    default: 50
    ```

    ```story
    name: current_date
    label: Current date
    type: date
    required: true
    ```

    ```story
    name: current_time
    label: Current time
    type: time
    required: true
    ```

    ```story
    name: system_datetime_approve
    label: Verify detected date/time
    type: datetime_approve
    required: true
    timezone_field: user_timezone
    ```

    ```story
    name: user_location_id
    label: Home location
    type: location
    required: false
    timezone_field: user_timezone
    ```
    """
)

story = parse_story_document(
    story_markdown,
    required_frontmatter_keys=["title", "type", "submit_endpoint"],
)

fields = []
for section in story.get("sections", []):
    section_title = section.get("title", "Section")
    section_content = section.get("content", "")
    for question in section.get("questions", []):
        fields.append(
            {
                **question,
                "label": f"{section_title}: {question.get('label', question.get('name', 'field'))}",
                "meta": {
                    **(question.get("meta") or {}),
                    "section_title": section_title,
                    "section_content": section_content,
                },
            }
        )

form_spec = {
    "title": story.get("frontmatter", {}).get("title", "TUI Story Form Demo"),
    "description": "Typeform-style staged TUI demo. Press Enter ↩ to continue.",
    "fields": fields,
}

if mode == "spec":
    print(json.dumps(form_spec, indent=2))
    raise SystemExit(0)

handler = get_form_handler()
result = handler.process_story_form(form_spec)
print("\nDemo result:\n")
print(json.dumps(result, indent=2, default=str))
PY
