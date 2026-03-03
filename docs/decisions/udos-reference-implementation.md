# uDOS TUI Reference Implementation Skeleton

Status: active supporting reference  
Updated: 2026-03-03

This is a supporting implementation sketch for the v1.5 `ucode` TUI lane.

## Overview

Flow: SelectOne → Input → Run → Streamed Output

Stack: - Go: Bubble Tea + Bubbles + Lip Gloss - Python: Backend JSONL
protocol emitter

------------------------------------------------------------------------

## Backend Stub (Python)

``` python
import json, sys, time, uuid

def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

while True:
    line = sys.stdin.readline()
    if not line:
        break
    msg = json.loads(line)
    if msg["type"] == "run":
        job_id = "job-" + uuid.uuid4().hex[:8]
        send({"v":1,"type":"ok","id":msg["id"],"job_id":job_id})
        for i in range(101):
            send({
                "v":1,"type":"event","id":job_id,"stream":"progress",
                "event":{"kind":"progress","pid":"p1","label":"Working","current":i,"total":100,"status":"running" if i<100 else "done"}
            })
            time.sleep(0.02)
        send({"v":1,"type":"done","id":job_id,"ok":True,"exit_code":0})
```

------------------------------------------------------------------------

## Go Structure

    tui/
      cmd/udos-tui/main.go
      internal/protocol/
      internal/render/

Main responsibilities:
- spawn backend subprocess
- send hello
- render selectors and inputs
- send run requests
- stream and render block/progress events
- exit cleanly

Current repo anchor:

- Go frontend: `tui/cmd/udos-tui/main.go`
- protocol bridge: `core/tui/protocol_bridge.py`
- launcher: `bin/udos-tui`
