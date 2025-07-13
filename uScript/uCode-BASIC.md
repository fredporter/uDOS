# uCode BASIC Command Set (Visual Basic–style)

## PRINT
- Syntax: `PRINT <string or {VAR}>`
- Description: Output a string or variable value to the console.
- Example: `PRINT "Hello, {USERNAME}!"`

## SET
- Syntax: `SET <var> = <value>`
- Description: Assign a value to a variable.
- Example: `SET MODE = "test"`

## IF / THEN / ELSE / END IF
- Syntax:
  ```
  IF <condition> THEN
      <commands>
  [ELSE
      <commands>]
  END IF
  ```
- Description: Conditional execution block.
- Example:
  ```
  IF MODE = "test" THEN
      PRINT "Test mode active."
  ELSE
      PRINT "Production mode."
  END IF
  ```

## FOR / NEXT
- Syntax:
  ```
  FOR <var> = <start> TO <end> [STEP <n>]
      <commands>
  NEXT
  ```
- Description: Looping.
- Example:
  ```
  FOR I = 1 TO 3
      PRINT "Loop: {I}"
  NEXT
  ```

## INCLUDE
- Syntax: `INCLUDE <filename>`
- Description: Import another script from `/uScript/` or `/uScript/examples/`.

## WAIT / SLEEP
- Syntax: `WAIT <seconds>`
- Description: Pause execution for a number of seconds.

## ANCHOR / GOTO (Labels)
- Syntax:
  ```
  LabelName:
      <commands>
  GOTO LabelName
  ```
- Description: Define a label/anchor and jump to it.
- Example:
  ```
  Start:
      PRINT "At Start"
      GOTO End
  End:
      PRINT "At End"
  ```

## LOAD DATASET
- Syntax: `LOAD DATASET <name> FROM "<path>"`
- Description: Load a JSON dataset from `/uScript/datasets/` for use in loops or lookups.
- Example:
  ```
  LOAD DATASET CITY FROM "datasets/cityMap.json"
  FOR I = 0 TO 2
      PRINT "City: {CITY[I].CITY}"
  NEXT
  ```

## LOG
- Syntax: `LOG <string or {VAR}>`
- Description: Append a message to `/uScript/logs/ucode.log`.
- Example: `LOG "User ran script at {NOW}"`

---

## Variable Substitution

- Use `{VARNAME}` in any string to substitute the value of a variable.
- Example: `PRINT "Welcome, {USERNAME}!"`

---

## Example Script

```vb
SET USERNAME = "otter"
PRINT "Welcome, {USERNAME}!"

IF MODE = "test" THEN
    PRINT "Test mode active."
    LOG "Test mode started by {USERNAME}"
ELSE
    PRINT "Production mode."
END IF

LOAD DATASET CITY FROM "datasets/cityMap.json"
FOR I = 0 TO 2
    PRINT "City: {CITY[I].CITY}"
NEXT
```

---

> All scripts, datasets, and logs should be placed in the `/uScript` subfolders:
> - Scripts: `/uScript/` or `/uScript/examples/`
> - Datasets: `/uScript/datasets/`
> - Variables: `/uScript/vars/`
> - Logs: `/uScript/logs/`
> - Templates: `/uScript/templates/`

...add more as needed!
