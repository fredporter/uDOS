# uScript VB Commands Reference

A comprehensive guide to Visual Basic-style commands in the uDOS ecosystem. These commands provide an intuitive interface for system operations, role management, and development tasks.

## Table of Contents

- [System Commands](#system-commands)
- [Role Management](#role-management)
- [Memory Operations](#memory-operations)
- [Knowledge Management](#knowledge-management)
- [Script Execution](#script-execution)
- [Template Operations](#template-operations)
- [Package Management](#package-management)
- [Mission Control](#mission-control)
- [Advanced Commands](#advanced-commands)
- [Error Handling](#error-handling)

## System Commands

### System.Status()
```vb
' Check overall system status
System.Status()
System.Status("verbose")
System.Status("summary")
```

### System.Version()
```vb
' Display version information
System.Version()
System.Version("uCORE")
System.Version("all")
```

### System.Info()
```vb
' System information and diagnostics
System.Info()
System.Info("hardware")
System.Info("environment")
System.Info("roles")
```

### System.Restart()
```vb
' Restart system components
System.Restart()
System.Restart("services")
System.Restart("memory")
```

## Role Management

### Role.Activate(roleName)
```vb
' Activate a specific role
Role.Activate("drone")
Role.Activate("ghost")
Role.Activate("imp")
Role.Activate("sorcerer")
Role.Activate("tomb")
Role.Activate("wizard")
```

### Role.Status(roleName)
```vb
' Check role status and permissions
Role.Status("drone")
Role.Status("all")
```

### Role.Switch(fromRole, toRole)
```vb
' Switch between roles
Role.Switch("ghost", "drone")
Role.Switch("current", "sorcerer")
```

### Role.Permissions(roleName)
```vb
' View role permissions
Role.Permissions("imp")
Role.Permissions("current")
Role.Permissions("all")
```

## Memory Operations

### Memory.Store(key, value)
```vb
' Store data in uMEMORY
Memory.Store("project_name", "uDOS-Development")
Memory.Store("user_preference", "dark_mode")
Memory.Store("session_data", dataObject)
```

### Memory.Retrieve(key)
```vb
' Retrieve data from uMEMORY
dim projectName = Memory.Retrieve("project_name")
dim userData = Memory.Retrieve("user_data")
```

### Memory.List()
```vb
' List stored memory items
Memory.List()
Memory.List("user*")
Memory.List("session*")
```

### Memory.Clear(pattern)
```vb
' Clear memory items
Memory.Clear("temp*")
Memory.Clear("session_data")
Memory.Clear("all")  ' Use with caution
```

## Knowledge Management

### Knowledge.Search(query)
```vb
' Search knowledge base
Knowledge.Search("role permissions")
Knowledge.Search("installation guide")
Knowledge.Search("API documentation")
```

### Knowledge.Add(topic, content)
```vb
' Add to knowledge base
Knowledge.Add("new_feature", "Description of new feature")
Knowledge.Add("troubleshooting", troubleshootingGuide)
```

### Knowledge.Update(topic, content)
```vb
' Update knowledge entry
Knowledge.Update("installation", updatedInstructions)
```

### Knowledge.Categories()
```vb
' List knowledge categories
Knowledge.Categories()
Knowledge.Categories("detailed")
```

## Script Execution

### Script.Run(scriptName)
```vb
' Execute uScript files
Script.Run("setup.us")
Script.Run("daily_maintenance.us")
Script.Run("backup_routine.us")
```

### Script.Execute(command)
```vb
' Execute inline commands
Script.Execute("ls -la")
Script.Execute("git status")
Script.Execute("npm install")
```

### Script.Schedule(scriptName, schedule)
```vb
' Schedule script execution
Script.Schedule("backup.us", "daily 2:00am")
Script.Schedule("cleanup.us", "weekly monday")
Script.Schedule("update.us", "monthly 1st")
```

### Script.List()
```vb
' List available scripts
Script.List()
Script.List("active")
Script.List("templates")
Script.List("user")
```

## Template Operations

### Template.Create(name, type)
```vb
' Create new templates
Template.Create("project_template", "project")
Template.Create("mission_template", "mission")
Template.Create("dashboard_template", "interface")
```

### Template.Load(templateName)
```vb
' Load existing template
dim projectTemplate = Template.Load("default_project")
dim missionTemplate = Template.Load("daily_mission")
```

### Template.Apply(templateName, targetPath)
```vb
' Apply template to location
Template.Apply("project_template", "/projects/new_project")
Template.Apply("config_template", "/config/")
```

### Template.List(category)
```vb
' List available templates
Template.List()
Template.List("project")
Template.List("mission")
Template.List("user")
```

## Package Management

### Package.Install(packageName)
```vb
' Install packages
Package.Install("advanced_tools")
Package.Install("development_kit")
Package.Install("security_module")
```

### Package.Update(packageName)
```vb
' Update packages
Package.Update("all")
Package.Update("core_system")
Package.Update("user_interface")
```

### Package.Remove(packageName)
```vb
' Remove packages
Package.Remove("unused_module")
Package.Remove("deprecated_tools")
```

### Package.List()
```vb
' List installed packages
Package.List()
Package.List("installed")
Package.List("available")
Package.List("updates")
```

## Mission Control

### Mission.Create(missionName, parameters)
```vb
' Create new mission
Mission.Create("daily_backup", backupParams)
Mission.Create("system_update", updateParams)
Mission.Create("security_scan", securityParams)
```

### Mission.Start(missionName)
```vb
' Start mission execution
Mission.Start("daily_backup")
Mission.Start("development_setup")
```

### Mission.Status(missionName)
```vb
' Check mission status
Mission.Status("daily_backup")
Mission.Status("all")
Mission.Status("active")
```

### Mission.Complete(missionName)
```vb
' Mark mission as complete
Mission.Complete("system_update")
Mission.Complete("security_scan")
```

## Advanced Commands

### Advanced.Benchmark()
```vb
' System performance benchmarking
Advanced.Benchmark()
Advanced.Benchmark("memory")
Advanced.Benchmark("disk")
Advanced.Benchmark("network")
```

### Advanced.Optimize(component)
```vb
' System optimization
Advanced.Optimize("memory")
Advanced.Optimize("storage")
Advanced.Optimize("performance")
Advanced.Optimize("all")
```

### Advanced.Backup(target, destination)
```vb
' Advanced backup operations
Advanced.Backup("full_system", "/backup/")
Advanced.Backup("user_data", "/external/backup/")
Advanced.Backup("configurations", "/config_backup/")
```

### Advanced.Restore(source, target)
```vb
' System restore operations
Advanced.Restore("/backup/system_20250820", "system")
Advanced.Restore("/backup/user_data", "user")
```

## Error Handling

### Try-Catch Blocks
```vb
Try
    Role.Activate("invalid_role")
Catch ex As RoleException
    Console.WriteLine("Role activation failed: " & ex.Message)
    Role.Activate("ghost")  ' Fallback to ghost role
End Try
```

### Error.Log(message, severity)
```vb
' Log error messages
Error.Log("Failed to load configuration", "warning")
Error.Log("Critical system failure", "error")
Error.Log("Unusual behavior detected", "info")
```

### Error.Report(errorDetails)
```vb
' Generate error reports
Error.Report(systemDiagnostics)
Error.Report("automated_report")
```

## Conditional Operations

### If-Then-Else Statements
```vb
' Role-based conditional execution
If Role.Current() = "sorcerer" Then
    Advanced.Optimize("all")
ElseIf Role.Current() = "drone" Then
    Mission.Start("automated_tasks")
Else
    System.Status("summary")
End If
```

### Select Case Statements
```vb
' Multi-condition handling
Select Case System.Status()
    Case "optimal"
        Mission.Start("maintenance")
    Case "warning"
        System.Optimize("performance")
    Case "critical"
        System.Restart("safe_mode")
    Case Else
        Error.Log("Unknown system state", "error")
End Select
```

## Loop Operations

### For Loops
```vb
' Iterate through role list
For Each role In Role.List()
    Console.WriteLine("Role: " & role & " - Level: " & Role.Level(role))
Next
```

### While Loops
```vb
' Monitor system status
While System.Status() <> "optimal"
    System.Optimize("incremental")
    Thread.Sleep(5000)  ' Wait 5 seconds
End While
```

## Variable Operations

### Variable Declaration and Assignment
```vb
' Declare and assign variables
Dim currentRole As String = Role.Current()
Dim systemMemory As Integer = System.Memory.Available()
Dim missionList As Array = Mission.List("active")
```

### Environment Variables
```vb
' Work with environment variables
Dim userHome As String = Environment.Variable("HOME")
Dim dosPath As String = Environment.Variable("UDOS_PATH")
Environment.Set("CUSTOM_VAR", "custom_value")
```

## File Operations

### File.Read(filePath)
```vb
' Read file contents
Dim configData As String = File.Read("/config/system.conf")
Dim userData As String = File.Read("~/user_settings.json")
```

### File.Write(filePath, content)
```vb
' Write to files
File.Write("/logs/activity.log", logEntry)
File.Write("~/backup/settings.txt", userSettings)
```

### File.Exists(filePath)
```vb
' Check file existence
If File.Exists("/config/custom.conf") Then
    Dim config = File.Read("/config/custom.conf")
Else
    File.Write("/config/custom.conf", defaultConfig)
End If
```

## Network Operations

### Network.Status()
```vb
' Check network connectivity
Network.Status()
Network.Status("detailed")
Network.Status("external")
```

### Network.Download(url, destination)
```vb
' Download files
Network.Download("https://updates.udos.dev/latest.zip", "/downloads/")
Network.Download("https://api.example.com/data.json", "/data/")
```

### Network.Upload(filePath, destination)
```vb
' Upload files
Network.Upload("/logs/system.log", "backup.server.com/logs/")
Network.Upload("/reports/daily.pdf", "reports.udos.dev/")
```

## Security Commands

### Security.Scan()
```vb
' Security scans
Security.Scan()
Security.Scan("vulnerabilities")
Security.Scan("permissions")
Security.Scan("network")
```

### Security.Encrypt(data, method)
```vb
' Data encryption
Dim encryptedData = Security.Encrypt(sensitiveData, "AES256")
Dim hashedPassword = Security.Hash(password, "SHA256")
```

### Security.Permissions.Check(resource, action)
```vb
' Permission checking
If Security.Permissions.Check("system_config", "write") Then
    File.Write("/config/system.conf", newConfig)
Else
    Error.Log("Insufficient permissions for config write", "warning")
End If
```

## Integration Commands

### Git.Status()
```vb
' Git repository operations
Git.Status()
Git.Add(".")
Git.Commit("Automated system update")
Git.Push("origin", "main")
```

### Docker.Status()
```vb
' Container operations
Docker.Status()
Docker.Start("udos_services")
Docker.Stop("udos_services")
Docker.Restart("udos_services")
```

### Database.Query(sql)
```vb
' Database operations
Dim results = Database.Query("SELECT * FROM user_sessions")
Database.Execute("UPDATE system_config SET value = 'updated' WHERE key = 'theme'")
```

## Troubleshooting Commands

### Diagnostic.Run(testSuite)
```vb
' System diagnostics
Diagnostic.Run("full")
Diagnostic.Run("memory")
Diagnostic.Run("permissions")
Diagnostic.Run("network")
```

### Debug.Mode(enabled)
```vb
' Debug mode control
Debug.Mode(True)   ' Enable debugging
Debug.Mode(False)  ' Disable debugging
Debug.Level("verbose")
```

### Log.View(logType, lines)
```vb
' Log viewing
Log.View("system", 50)
Log.View("error", 25)
Log.View("all", 100)
```

## Examples and Use Cases

### Daily System Maintenance
```vb
' Daily maintenance routine
Sub DailyMaintenance()
    Try
        Console.WriteLine("Starting daily maintenance...")
        
        ' Activate appropriate role
        Role.Activate("drone")
        
        ' System cleanup
        System.Optimize("cleanup")
        
        ' Update knowledge base
        Knowledge.Update("maintenance_log", DateTime.Now.ToString())
        
        ' Backup critical data
        Advanced.Backup("configurations", "/daily_backup/")
        
        ' Generate report
        Mission.Create("maintenance_report", reportParams)
        Mission.Start("maintenance_report")
        
        Console.WriteLine("Daily maintenance completed successfully.")
        
    Catch ex As Exception
        Error.Log("Daily maintenance failed: " & ex.Message, "error")
        Error.Report(ex)
    End Try
End Sub
```

### Project Setup Automation
```vb
' Automated project setup
Sub SetupNewProject(projectName As String, projectType As String)
    Try
        ' Activate development role
        Role.Activate("imp")
        
        ' Create project from template
        Template.Apply(projectType & "_template", "/projects/" & projectName)
        
        ' Initialize project memory
        Memory.Store("current_project", projectName)
        Memory.Store("project_type", projectType)
        
        ' Set up mission tracking
        Mission.Create("project_" & projectName, projectParams)
        
        ' Update knowledge base
        Knowledge.Add("project_" & projectName, "Project created: " & DateTime.Now.ToString())
        
        Console.WriteLine("Project " & projectName & " setup complete.")
        
    Catch ex As Exception
        Error.Log("Project setup failed: " & ex.Message, "error")
    End Try
End Sub
```

### Security Audit
```vb
' Comprehensive security audit
Sub SecurityAudit()
    Try
        ' Activate security role
        Role.Activate("sorcerer")
        
        ' Run security scans
        Security.Scan("full")
        
        ' Check all role permissions
        For Each role In Role.List()
            Dim permissions = Role.Permissions(role)
            Console.WriteLine("Role: " & role & " - Permissions: " & permissions)
        Next
        
        ' Verify system integrity
        Diagnostic.Run("security")
        
        ' Generate security report
        Mission.Create("security_audit_" & DateTime.Now.ToString("yyyyMMdd"), auditParams)
        Mission.Start("security_audit_" & DateTime.Now.ToString("yyyyMMdd"))
        
        Console.WriteLine("Security audit completed.")
        
    Catch ex As Exception
        Error.Log("Security audit failed: " & ex.Message, "critical")
        Error.Report(ex)
    End Try
End Sub
```

## Best Practices

### Error Handling
- Always use Try-Catch blocks for critical operations
- Log errors with appropriate severity levels
- Provide fallback options for failed operations
- Generate detailed error reports for debugging

### Role Management
- Activate appropriate roles for specific tasks
- Check role permissions before executing privileged operations
- Switch roles when necessary for task optimization
- Document role usage patterns

### Memory Management
- Store frequently accessed data in Memory
- Use descriptive keys for stored values
- Clean up temporary memory items regularly
- Monitor memory usage for optimization

### Security Considerations
- Validate user input and permissions
- Use encryption for sensitive data
- Regularly audit system security
- Follow principle of least privilege

### Performance Optimization
- Use appropriate roles for tasks
- Batch operations when possible
- Monitor system resources
- Optimize frequently used operations

---

*This reference guide provides comprehensive coverage of uScript VB Commands for the uDOS ecosystem. For additional examples and advanced usage patterns, consult the uDOS documentation library or contact your system administrator.*
