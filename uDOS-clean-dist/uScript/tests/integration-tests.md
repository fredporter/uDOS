# uScript Integration Tests

Integration tests for uScript with uDOS system components and external tools.

---
title: "uScript Integration Test Suite"
type: "integration_testing"
version: "1.0.0"
author: "uDOS System"
---

## 🔗 System Integration Tests

```uScript
' uScript Integration Test Suite
' Tests integration with uDOS components and external systems

SET test_suite_name = "uScript Integration Tests"
SET test_start_time = NOW()
SET total_tests = 0
SET passed_tests = 0
SET failed_tests = 0

LOG_INFO "Starting " + test_suite_name + " at " + test_start_time

' Test 1: uMemory Integration
LOG_INFO "Test 1: uMemory Integration"
SET total_tests = total_tests + 1

SET test_mission_id = "integration-test-" + generate_id()
CREATE MISSION test_mission_id

' Test mission creation
IF file_exists("./uMemory/missions/" + test_mission_id + ".md") THEN
    LOG_INFO "✅ Mission creation successful"
    
    ' Test move creation
    CREATE MOVE test_mission_id + "/test-move" {
        "description": "Integration test move",
        "status": "completed",
        "created": NOW()
    }
    
    IF file_exists("./uMemory/moves/" + test_mission_id + "-test-move.md") THEN
        LOG_INFO "✅ Move creation successful"
        
        ' Test milestone creation
        CREATE MILESTONE test_mission_id + "/test-milestone"
        
        IF file_exists("./uMemory/milestones/" + test_mission_id + "-test-milestone.md") THEN
            LOG_INFO "✅ Test 1 PASSED: uMemory integration working"
            SET passed_tests = passed_tests + 1
        ELSE
            LOG_ERROR "❌ Test 1 FAILED: Milestone creation failed"
            SET failed_tests = failed_tests + 1
        END IF
    ELSE
        LOG_ERROR "❌ Test 1 FAILED: Move creation failed"
        SET failed_tests = failed_tests + 1
    END IF
ELSE
    LOG_ERROR "❌ Test 1 FAILED: Mission creation failed"
    SET failed_tests = failed_tests + 1
END IF

' Test 2: File System Operations
LOG_INFO "Test 2: File System Operations"
SET total_tests = total_tests + 1

SET test_dir = "./uMemory/test-temp"
SET test_file = test_dir + "/integration-test.txt"
SET test_content = "Integration test content - " + NOW()

' Create directory
create_directory(test_dir)
IF directory_exists(test_dir) THEN
    LOG_INFO "✅ Directory creation successful"
    
    ' Write file
    write_file(test_file, test_content)
    IF file_exists(test_file) THEN
        LOG_INFO "✅ File write successful"
        
        ' Read file
        SET read_content = read_file(test_file)
        IF read_content = test_content THEN
            LOG_INFO "✅ File read successful"
            
            ' Delete file and directory
            delete_file(test_file)
            remove_directory(test_dir)
            
            IF NOT file_exists(test_file) AND NOT directory_exists(test_dir) THEN
                LOG_INFO "✅ Test 2 PASSED: File system operations working"
                SET passed_tests = passed_tests + 1
            ELSE
                LOG_ERROR "❌ Test 2 FAILED: File/directory cleanup failed"
                SET failed_tests = failed_tests + 1
            END IF
        ELSE
            LOG_ERROR "❌ Test 2 FAILED: File content mismatch"
            SET failed_tests = failed_tests + 1
        END IF
    ELSE
        LOG_ERROR "❌ Test 2 FAILED: File write failed"
        SET failed_tests = failed_tests + 1
    END IF
ELSE
    LOG_ERROR "❌ Test 2 FAILED: Directory creation failed"
    SET failed_tests = failed_tests + 1
END IF

' Test 3: uCode Command Integration
LOG_INFO "Test 3: uCode Command Integration"
SET total_tests = total_tests + 1

' Test system health check
SET health_result = system_status()
IF health_result != "" THEN
    LOG_INFO "✅ System status check successful: " + health_result
    
    ' Test shell command execution
    SET command_output = RUN "echo 'Integration test command'"
    IF CONTAINS(command_output, "Integration test") THEN
        LOG_INFO "✅ Shell command execution successful"
        
        ' Test uCode script execution
        SET script_result = RUN "./uCode/check.sh version"
        IF script_result != "" THEN
            LOG_INFO "✅ Test 3 PASSED: uCode integration working"
            SET passed_tests = passed_tests + 1
        ELSE
            LOG_ERROR "❌ Test 3 FAILED: uCode script execution failed"
            SET failed_tests = failed_tests + 1
        END IF
    ELSE
        LOG_ERROR "❌ Test 3 FAILED: Shell command execution failed"
        SET failed_tests = failed_tests + 1
    END IF
ELSE
    LOG_ERROR "❌ Test 3 FAILED: System status check failed"
    SET failed_tests = failed_tests + 1
END IF

' Test 4: Template System Integration
LOG_INFO "Test 4: Template System Integration"
SET total_tests = total_tests + 1

' Test template loading
SET template_path = "./uTemplate/mission-template.md"
IF file_exists(template_path) THEN
    LOG_INFO "✅ Template file found"
    
    ' Test template variable substitution
    SET template_vars = {
        "mission_name": "Integration Test Mission",
        "author": "Test Suite",
        "date": TODAY()
    }
    
    SET rendered_template = render_template(template_path, template_vars)
    IF CONTAINS(rendered_template, "Integration Test Mission") THEN
        LOG_INFO "✅ Template rendering successful"
        
        ' Test template saving
        SET output_file = "./uMemory/test-temp/rendered-template.md"
        write_file(output_file, rendered_template)
        
        IF file_exists(output_file) THEN
            LOG_INFO "✅ Test 4 PASSED: Template system integration working"
            SET passed_tests = passed_tests + 1
            delete_file(output_file)
        ELSE
            LOG_ERROR "❌ Test 4 FAILED: Template output save failed"
            SET failed_tests = failed_tests + 1
        END IF
    ELSE
        LOG_ERROR "❌ Test 4 FAILED: Template rendering failed"
        SET failed_tests = failed_tests + 1
    END IF
ELSE
    LOG_WARN "⚠️ Test 4 SKIPPED: Template file not found"
    SET total_tests = total_tests - 1
END IF

' Test 5: Dashboard Integration
LOG_INFO "Test 5: Dashboard Integration"
SET total_tests = total_tests + 1

' Test dashboard data update
SET dashboard_data = {
    "test_suite": test_suite_name,
    "status": "running",
    "progress": (passed_tests / total_tests) * 100,
    "timestamp": NOW()
}

SET dashboard_file = "./uMemory/dashboard/integration-test.json"
write_json_file(dashboard_file, dashboard_data)

IF file_exists(dashboard_file) THEN
    LOG_INFO "✅ Dashboard data written"
    
    ' Test dashboard message
    LOG_DASHBOARD "🧪 Integration tests in progress"
    
    ' Test dashboard refresh
    RUN "./uCode/dash.sh"
    
    LOG_INFO "✅ Test 5 PASSED: Dashboard integration working"
    SET passed_tests = passed_tests + 1
    
    ' Cleanup
    delete_file(dashboard_file)
ELSE
    LOG_ERROR "❌ Test 5 FAILED: Dashboard data write failed"
    SET failed_tests = failed_tests + 1
END IF

' Test 6: Logging System Integration
LOG_INFO "Test 6: Logging System Integration"
SET total_tests = total_tests + 1

' Test different log levels
LOG_DEBUG "Debug message from integration test"
LOG_INFO "Info message from integration test"
LOG_WARN "Warning message from integration test"

' Test mission-specific logging
LOG_MISSION test_mission_id, "Mission log from integration test"

' Test structured logging
LOG_STRUCTURED "INFO", "integration_test", {
    "test_name": "logging_integration",
    "status": "running",
    "data": "test_data"
}

' Check if logs were written
SET log_files_count = count_files("./uMemory/logs/*integration*")
IF log_files_count > 0 THEN
    LOG_INFO "✅ Test 6 PASSED: Logging system integration working"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 6 FAILED: Logging integration failed"
    SET failed_tests = failed_tests + 1
END IF

' Test 7: JSON/Data Processing Integration
LOG_INFO "Test 7: JSON/Data Processing Integration"
SET total_tests = total_tests + 1

' Test JSON parsing and manipulation
SET test_json_data = {
    "users": [
        {"name": "Alice", "score": 95},
        {"name": "Bob", "score": 87},
        {"name": "Charlie", "score": 92}
    ],
    "metadata": {
        "total": 3,
        "average": 91.33
    }
}

SET json_file = "./uMemory/test-temp/integration-data.json"
write_json_file(json_file, test_json_data)

IF file_exists(json_file) THEN
    LOG_INFO "✅ JSON write successful"
    
    ' Read and parse JSON
    SET parsed_data = read_json_file(json_file)
    IF parsed_data.metadata.total = 3 THEN
        LOG_INFO "✅ JSON read and parse successful"
        
        ' Test data processing
        SET high_scorers = filter_array(parsed_data.users, "score > 90")
        IF LEN(high_scorers) = 2 THEN
            LOG_INFO "✅ Test 7 PASSED: JSON/Data processing integration working"
            SET passed_tests = passed_tests + 1
        ELSE
            LOG_ERROR "❌ Test 7 FAILED: Data filtering failed"
            SET failed_tests = failed_tests + 1
        END IF
    ELSE
        LOG_ERROR "❌ Test 7 FAILED: JSON parsing failed"
        SET failed_tests = failed_tests + 1
    END IF
    
    delete_file(json_file)
ELSE
    LOG_ERROR "❌ Test 7 FAILED: JSON write failed"
    SET failed_tests = failed_tests + 1
END IF

' Cleanup Test Data
LOG_INFO "Cleaning up test data..."
IF file_exists("./uMemory/missions/" + test_mission_id + ".md") THEN
    delete_file("./uMemory/missions/" + test_mission_id + ".md")
END IF

IF file_exists("./uMemory/moves/" + test_mission_id + "-test-move.md") THEN
    delete_file("./uMemory/moves/" + test_mission_id + "-test-move.md")
END IF

IF file_exists("./uMemory/milestones/" + test_mission_id + "-test-milestone.md") THEN
    delete_file("./uMemory/milestones/" + test_mission_id + "-test-milestone.md")
END IF

' Test Summary
SET test_end_time = NOW()
SET test_duration = time_diff(test_end_time, test_start_time)
SET success_rate = (passed_tests / total_tests) * 100

LOG_INFO "Integration Test Suite Completed"
LOG_INFO "================================="
LOG_INFO "Total Tests: " + total_tests
LOG_INFO "Passed: " + passed_tests
LOG_INFO "Failed: " + failed_tests
LOG_INFO "Success Rate: " + success_rate + "%"
LOG_INFO "Duration: " + test_duration + "ms"

' Generate Integration Test Report
SET report_file = "./uMemory/tests/integration-test-" + TODAY() + ".md"
SET report_content = "# uScript Integration Test Report\n\n"
SET report_content = report_content + "**Date:** " + TODAY() + "\n"
SET report_content = report_content + "**Duration:** " + test_duration + "ms\n\n"
SET report_content = report_content + "## Test Results\n\n"
SET report_content = report_content + "- **Total Tests:** " + total_tests + "\n"
SET report_content = report_content + "- **Passed:** " + passed_tests + "\n"
SET report_content = report_content + "- **Failed:** " + failed_tests + "\n"
SET report_content = report_content + "- **Success Rate:** " + success_rate + "%\n\n"

SET report_content = report_content + "## Integration Points Tested\n\n"
SET report_content = report_content + "1. **uMemory Integration** - Mission/Move/Milestone creation\n"
SET report_content = report_content + "2. **File System Operations** - Read/Write/Delete operations\n"
SET report_content = report_content + "3. **uCode Command Integration** - System commands and scripts\n"
SET report_content = report_content + "4. **Template System** - Template rendering and variables\n"
SET report_content = report_content + "5. **Dashboard Integration** - Data updates and messaging\n"
SET report_content = report_content + "6. **Logging System** - Multi-level and structured logging\n"
SET report_content = report_content + "7. **JSON/Data Processing** - Data manipulation and filtering\n\n"

IF failed_tests = 0 THEN
    SET report_content = report_content + "✅ **All integration tests passed successfully!**\n"
    LOG_DASHBOARD "✅ uScript integration tests: All " + total_tests + " tests passed"
ELSE
    SET report_content = report_content + "❌ **" + failed_tests + " integration test(s) failed - system review required**\n"
    LOG_DASHBOARD "⚠️ uScript integration tests: " + failed_tests + " failed out of " + total_tests
END IF

write_file(report_file, report_content)
LOG_INFO "Integration test report saved: " + report_file

' Performance Logging
LOG_PERFORMANCE "integration_tests", test_duration

IF failed_tests = 0 THEN
    LOG_INFO "🎉 All integration tests passed - uScript system integration working correctly!"
    EXIT 0
ELSE
    LOG_ERROR "⚠️ Some integration tests failed - system integration needs attention"
    EXIT 1
END IF
```

## 🔗 Integration Points

### Core System Integration
- **uMemory**: Mission, move, and milestone management
- **uCode**: Command execution and system interaction
- **uTemplate**: Template rendering and variable substitution
- **Dashboard**: Data updates and status messaging

### External System Integration
- **File System**: Read/write operations and directory management
- **Shell Commands**: System command execution and output capture
- **JSON Processing**: Data serialization and manipulation
- **Logging**: Multi-level and structured logging systems

## 📊 Expected Results

All integration tests should pass with 100% success rate. Failures indicate:
- Component interface issues
- File system permission problems
- Missing dependencies or system tools
- Configuration or setup problems

## 🎯 Usage

Run this integration test suite to validate system connectivity:

```bash
./uCode/ucode.sh run uScript/tests/integration-tests.md
```

---

*This integration test suite ensures uScript works correctly with all uDOS system components and external dependencies.*
