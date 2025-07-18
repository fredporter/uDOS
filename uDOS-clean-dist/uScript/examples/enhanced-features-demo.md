# 🚀 Enhanced uDOS Demo - Error Handling & Shortcodes

**Version**: 1.7.1 Enhanced  
**Created**: $(date '+%Y-%m-%d %H:%M:%S')  
**Purpose**: Demonstrate enhanced error handling and shortcode system

## 🧭 Overview

This script demonstrates the new enhanced features of uDOS:
- **Comprehensive error handling** with automatic recovery
- **Shortcode system** for seamless script execution
- **Containerized bash execution** for security
- **Performance tracking** and logging
- **Retry mechanisms** for robust operation

## 🔧 Demo Script

```uScript
' Enhanced uScript Demo with Error Handling
SET demo_name = "Enhanced uDOS Features Demo"
SET demo_version = "1.7.1"
SET start_time = NOW()

LOG_INFO "Starting " + demo_name + " v" + demo_version

' 1. Test Error Handling System
LOG_INFO "=== Testing Error Handling ==="

TRY
    ' Simulate a file operation that might fail
    SET test_file = "./uMemory/test/demo-file.txt"
    
    IF NOT file_exists(dirname(test_file)) THEN
        LOG_WARN "Test directory doesn't exist - creating it"
        CREATE_DIRECTORY dirname(test_file)
    END IF
    
    WRITE_FILE test_file, "Hello from Enhanced uDOS!"
    LOG_INFO "✅ File operation successful"
    
CATCH file_error
    LOG_ERROR "File operation failed: " + file_error
    ' Error handler will attempt automatic recovery
END TRY

' 2. Test Shortcode System
LOG_INFO "=== Testing Shortcode System ==="

' These shortcodes will be processed by the shortcode system
LOG_INFO "Executing shortcode examples..."

' Check system health
[check:health]

' List available scripts
[run:list-scripts]

' Execute a bash command safely
[bash:echo "Hello from containerized bash!"]

' Create a mission using shortcode
[mission:create name=demo-mission]

' 3. Test Container System
LOG_INFO "=== Testing Container System ==="

SET container_commands = [
    "ls -la",
    "pwd", 
    "echo 'Container test successful'",
    "date"
]

FOR EACH cmd IN container_commands
    LOG_INFO "Executing in container: " + cmd
    TRY
        [bash:$cmd]
        LOG_INFO "✅ Container command successful"
    CATCH container_error
        LOG_ERROR "Container command failed: " + container_error
    END TRY
NEXT cmd

' 4. Test Performance Tracking
LOG_INFO "=== Testing Performance Tracking ==="

SET processing_start = NOW()

' Simulate data processing
FOR i = 1 TO 100
    SET data_item = "item_" + i
    LOG_DEBUG "Processing " + data_item
    
    ' Simulate processing time
    SLEEP 0.01
NEXT i

SET processing_duration = NOW() - processing_start
LOG_PERFORMANCE "data_processing", processing_duration

' 5. Test Mission Integration
LOG_INFO "=== Testing Mission Integration ==="

CREATE MISSION "enhanced-features-demo"
CREATE MOVE "enhanced-features-demo/error-handling-test" {
    "description": "Tested error handling system",
    "status": "completed",
    "timestamp": NOW()
}

CREATE MOVE "enhanced-features-demo/shortcode-test" {
    "description": "Tested shortcode system", 
    "status": "completed",
    "timestamp": NOW()
}

CREATE MILESTONE "enhanced-features-demo/demo-complete"

' 6. Final Summary
SET end_time = NOW()
SET total_duration = end_time - start_time

LOG_INFO "🎉 Enhanced Features Demo Completed!"
LOG_INFO "Duration: " + (total_duration/1000) + " seconds"
LOG_DASHBOARD "✅ Enhanced uDOS demo completed successfully"

' Exit with success
EXIT 0
```

## 🔍 Expected Outputs

This demo will:
1. **Create test files** with error recovery if directories don't exist
2. **Execute shortcodes** to demonstrate the new syntax
3. **Run containerized commands** safely
4. **Track performance** metrics
5. **Create mission entries** for tracking
6. **Log comprehensive information** for debugging

## 🎯 Usage

Run this demo with the enhanced script runner:

```bash
# Using enhanced RUN command in uCode
RUN enhanced-features-demo

# Using enhanced script runner directly  
./uScript/system/enhanced-script-runner.sh run ./uScript/examples/enhanced-features-demo.md

# Using shortcode syntax
[run:enhanced-features-demo]
```

## 🛡️ Error Handling Features

- **Automatic retry** on transient failures
- **Recovery procedures** for common issues
- **Comprehensive logging** of all errors
- **Performance impact tracking**
- **User-friendly error messages**

## 🔧 Shortcode Examples

```
[run:hello-world]           - Execute hello-world uScript
[bash:find . -name "*.md"]  - Run bash command in container
[check:health]              - Perform system health check
[mission:create name=test]  - Create new mission
[data:csv file=data.csv]    - Process CSV file
[error:stats]               - Show error statistics
```

---

*This demo showcases the enhanced uDOS capabilities with robust error handling, shortcode system, and containerized execution.*
