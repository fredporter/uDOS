
"""
Emit a single-line uDOS DEV SUMMARY log line for Copilot/AI summaries.
Reads sandbox/user.json (if present) for context; never touches .env.
"""
from core.dev_logger import dev_log_path, dev_log
import sys

def main():
    # Inputs via CLI args or defaults:
    # usage: python -m core.copilot_summary "short summary" [ms] [code] [tizo] [zoom]
    summary = sys.argv[1] if len(sys.argv) > 1 else "no changes"
    ms = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    code = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    tizo = sys.argv[4] if len(sys.argv) > 4 else None
    zoom = int(sys.argv[5]) if len(sys.argv) > 5 else None

    path = dev_log_path(tizo=tizo, zoom=zoom)
    with open(path, "a", encoding="utf-8") as fp:
        dev_log(fp, tizo, zoom, "DEV SUMMARY", code, ms, summary, with_user_ctx=True)
    print(path)

if __name__ == "__main__":
    main()
