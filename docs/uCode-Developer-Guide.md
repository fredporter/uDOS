# uCode Script Developer Guide

## 📘 Visual Basic Style Syntax

uCode scripts use familiar Visual Basic-style syntax for easy development and maintenance.

### **1. Variable Declaration**
```vb
' Declare variables with DIM
DIM message AS STRING
DIM counter AS INTEGER  
DIM result AS BOOLEAN
DIM items AS ARRAY

' Initialize variables
SET message = "Hello uDOS"
SET counter = 0
SET result = TRUE
```

### **2. Function Definitions**
```vb
' Function declaration with return type
FUNCTION GetSystemStatus() AS STRING
    DIM status AS STRING
    SET status = "System operational"
    RETURN status
END FUNCTION

' Function with parameters
FUNCTION CalculateSize(path AS STRING, recursive AS BOOLEAN) AS INTEGER
    DIM size AS INTEGER
    ' Function logic here
    RETURN size
END FUNCTION
```

### **3. Control Structures**

#### **IF Statements**
```vb
IF condition THEN
    ' Execute if true
ELSEIF another_condition THEN
    ' Execute if second condition true
ELSE
    ' Execute if all false
END IF
```

#### **SELECT CASE**
```vb
SELECT CASE argument
    CASE "generate"
        CALL GenerateTree()
    CASE "display"
        CALL DisplayTree()
    CASE "export"
        CALL ExportTree()
    CASE ELSE
        PRINT "Unknown command"
END SELECT
```

#### **FOR Loops**
```vb
FOR i = 1 TO 10
    PRINT "Item " + STR(i)
NEXT i

FOR EACH item IN collection
    PRINT item
NEXT item
```

#### **WHILE Loops**
```vb
WHILE condition
    ' Loop body
WEND
```

### **4. Built-in Functions**

#### **String Functions**
```vb
LEN(string)           ' String length
MID(string, start, length)  ' Substring
UPPER(string)         ' Uppercase
LOWER(string)         ' Lowercase
TRIM(string)          ' Remove whitespace
```

#### **System Functions**
```vb
EXEC(command)         ' Execute shell command
READ_FILE(path)       ' Read file contents
WRITE_FILE(path, content)  ' Write to file
FILE_EXISTS(path)     ' Check if file exists
DIR_EXISTS(path)      ' Check if directory exists
```

#### **uDOS Functions**
```vb
GET_TERMINAL_SIZE()   ' Current terminal dimensions
GET_USER_ROLE()       ' Current user role
GET_INSTALLATION()    ' Current installation type
RENDER_PANEL(config)  ' Render ASCII panel
LOG_MESSAGE(level, text)  ' Write to system log
```

## 🎯 Script Structure Template

```vb
' =====================================================
' SCRIPT NAME: YourScript.ucode
' PURPOSE: Brief description of functionality
' AUTHOR: Your name
' VERSION: 1.0
' DEPENDENCIES: List any required files/scripts
' =====================================================

' === VARIABLE DECLARATIONS ===
DIM script_name AS STRING
DIM version AS STRING
DIM debug_mode AS BOOLEAN

' === INITIALIZATION ===
SET script_name = "YourScript"
SET version = "1.0"
SET debug_mode = FALSE

' === MAIN EXECUTION FUNCTION ===
FUNCTION Main(arguments AS ARRAY) AS INTEGER
    DIM command AS STRING
    SET command = arguments[0]
    
    SELECT CASE command
        CASE "start"
            RETURN StartProcess()
        CASE "stop"
            RETURN StopProcess()
        CASE "status"
            RETURN ShowStatus()
        CASE ELSE
            CALL ShowHelp()
            RETURN 1
    END SELECT
END FUNCTION

' === HELPER FUNCTIONS ===
FUNCTION StartProcess() AS INTEGER
    ' Implementation here
    RETURN 0
END FUNCTION

FUNCTION StopProcess() AS INTEGER
    ' Implementation here
    RETURN 0
END FUNCTION

FUNCTION ShowStatus() AS INTEGER
    ' Implementation here
    RETURN 0
END FUNCTION

FUNCTION ShowHelp() AS VOID
    PRINT "Usage: " + script_name + " [start|stop|status]"
    PRINT "  start  - Start the process"
    PRINT "  stop   - Stop the process"  
    PRINT "  status - Show current status"
END FUNCTION

' === SCRIPT ENTRY POINT ===
' The Main function is automatically called by uCode interpreter
' with command line arguments passed as array
```

## 🏗️ Advanced Patterns

### **1. Configuration Management**
```vb
' Load configuration from JSON
FUNCTION LoadConfig() AS OBJECT
    DIM config AS OBJECT
    IF FILE_EXISTS("config.json") THEN
        SET config = JSON_LOAD("config.json")
    ELSE
        SET config = GetDefaultConfig()
        CALL JSON_SAVE("config.json", config)
    END IF
    RETURN config
END FUNCTION
```

### **2. Error Handling**
```vb
FUNCTION SafeOperation() AS INTEGER
    ON ERROR GOTO ErrorHandler
    
    ' Risky operation here
    EXEC("some_command")
    
    RETURN 0
    
ErrorHandler:
    LOG_MESSAGE("ERROR", "Operation failed: " + ERROR_MESSAGE)
    RETURN 1
END FUNCTION
```

### **3. Panel Rendering**
```vb
FUNCTION RenderDashboard() AS VOID
    DIM panel_config AS OBJECT
    SET panel_config = CreateObject()
    
    ' Configure panel
    panel_config.title = "System Dashboard"
    panel_config.width = 80
    panel_config.height = 24
    panel_config.border = TRUE
    
    ' Add content sections
    CALL panel_config.AddSection("System Status", GetSystemStatus())
    CALL panel_config.AddSection("Memory Usage", GetMemoryInfo())
    CALL panel_config.AddSection("Disk Usage", GetDiskInfo())
    
    ' Render to terminal
    CALL RENDER_PANEL(panel_config)
END FUNCTION
```

### **4. Data Processing**
```vb
FUNCTION ProcessLogFile(filename AS STRING) AS ARRAY
    DIM lines AS ARRAY
    DIM processed AS ARRAY
    DIM line AS STRING
    
    SET lines = READ_file_lines(filename)
    SET processed = CreateArray()
    
    FOR EACH line IN lines
        IF LEN(TRIM(line)) > 0 THEN
            CALL processed.Add(ProcessLogLine(line))
        END IF
    NEXT line
    
    RETURN processed
END FUNCTION
```

## 🛠️ Debugging and Testing

### **Debug Output**
```vb
IF debug_mode THEN
    PRINT "DEBUG: Variable value = " + STR(variable)
    LOG_MESSAGE("DEBUG", "Function entered: " + FUNCTION_NAME)
END IF
```

### **Unit Testing Pattern**
```vb
FUNCTION RunTests() AS INTEGER
    DIM passed AS INTEGER
    DIM failed AS INTEGER
    
    SET passed = 0
    SET failed = 0
    
    ' Test 1
    IF TestFunction1() THEN
        SET passed = passed + 1
        PRINT "✅ Test 1 passed"
    ELSE
        SET failed = failed + 1
        PRINT "❌ Test 1 failed"
    END IF
    
    ' Report results
    PRINT "Tests: " + STR(passed) + " passed, " + STR(failed) + " failed"
    
    IF failed = 0 THEN
        RETURN 0
    ELSE
        RETURN 1
    END IF
END FUNCTION
```

## 🚀 Best Practices

### **1. Naming Conventions**
- **Functions**: PascalCase (`GetSystemStatus`)
- **Variables**: snake_case (`system_status`)
- **Constants**: UPPER_CASE (`MAX_RETRIES`)

### **2. File Organization**
- One main purpose per script
- Group related functions together
- Keep scripts under 300 lines when possible

### **3. Performance Tips**
- Cache expensive operations
- Use local variables in loops
- Avoid repeated file system calls

### **4. Error Handling**
- Always check file operations
- Provide meaningful error messages
- Log errors for debugging

### **5. Documentation**
- Comment complex logic
- Document function parameters
- Include usage examples

This guide provides the foundation for developing robust uCode scripts that integrate seamlessly with the uDOS modular architecture.
