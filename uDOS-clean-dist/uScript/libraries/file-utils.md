# File Utilities Library

Collection of file manipulation functions for uScript.

## Functions

### file_exists(path)
Check if a file exists at the given path.

```uScript
IF file_exists("./uMemory/missions/my-mission.md") THEN
    LOG "Mission file found"
ELSE
    LOG "Mission file not found"
END IF
```

### count_files(pattern)
Count files matching a glob pattern.

```uScript
SET mission_count = count_files("./uMemory/missions/*.md")
LOG "Total missions: " + mission_count
```

### file_age(path)
Get the age of a file in days.

```uScript
SET age = file_age("./uMemory/logs/last-run.log")
IF age > 7 THEN
    LOG "Log file is older than a week"
END IF
```

### copy_file(source, destination)
Copy a file from source to destination.

```uScript
copy_file("./templates/mission-template.md", "./uMemory/missions/new-mission.md")
LOG "Mission template copied"
```

### delete_file(path)
Delete a file safely with confirmation.

```uScript
IF file_age("./temp/old-data.tmp") > 30 THEN
    delete_file("./temp/old-data.tmp")
    LOG "Old temporary file deleted"
END IF
```

### read_file_lines(path)
Read file contents as an array of lines.

```uScript
SET lines = read_file_lines("./uMemory/moves/recent-moves.md")
FOR i = 1 TO LEN(lines)
    LOG "Line " + i + ": " + lines[i]
NEXT i
```

### write_file(path, content)
Write content to a file.

```uScript
SET report = "Mission Status Report\n" + "Generated: " + NOW()
write_file("./uMemory/reports/status.md", report)
LOG "Report written to file"
```

---

*These utilities provide safe, uDOS-integrated file operations with automatic logging and error handling.*
