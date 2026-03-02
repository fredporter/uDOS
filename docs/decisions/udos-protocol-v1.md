# uDOS TUI Protocol v1

Status: active supporting protocol  
Updated: 2026-03-03

This is the current structured message protocol for the v1.5 `ucode` TUI lane.

## Envelope (Required Fields)

-   `v` (int): protocol version (1)
-   `type` (string): message type
-   `id` (string): unique identifier
-   `ts` (string, optional): ISO-8601 timestamp

All messages are UTF-8 JSON, one per line (JSONL).

------------------------------------------------------------------------

## TUI → Backend

### hello

``` json
{"v":1,"type":"hello","id":"1","client":{"name":"udos-tui","version":"0.1.0"},"caps":{"tty":true,"width":78,"color":"256","paste":"bracketed"}}
```

### select_one

``` json
{
  "v":1,
  "type":"select_one",
  "id":"2",
  "title":"Select profile",
  "items":[{"key":"dev","label":"Dev"},{"key":"prod","label":"Prod"}],
  "ui":{"filter":true,"default":"dev"}
}
```

### input

``` json
{
  "v":1,
  "type":"input",
  "id":"3",
  "title":"Project name",
  "placeholder":"my-project",
  "default":"",
  "ui":{"multiline":false}
}
```

### run

``` json
{
  "v":1,
  "type":"run",
  "id":"4",
  "job":"demo.install",
  "args":{"profile":"dev","name":"my-project"}
}
```

------------------------------------------------------------------------

## Backend → TUI

### result

``` json
{"v":1,"type":"result","id":"2","value":"dev"}
```

### event (block)

``` json
{
  "v":1,
  "type":"event",
  "id":"job-123",
  "stream":"main",
  "event":{"kind":"block","title":"Runner","style":"info","lines":["Starting..."]}
}
```

### event (progress)

``` json
{
  "v":1,
  "type":"event",
  "id":"job-123",
  "stream":"progress",
  "event":{"kind":"progress","pid":"p1","label":"Working","current":50,"total":100,"status":"running"}
}
```

### done

``` json
{"v":1,"type":"done","id":"job-123","ok":true,"exit_code":0}
```

------------------------------------------------------------------------

## Rules

-   Unknown fields MUST be ignored.
-   Backend MUST flush stdout after each message.
-   `id` ties request/response pairs.
