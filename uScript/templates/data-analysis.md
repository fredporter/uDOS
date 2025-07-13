# Data Analysis Script Template

Template for creating data analysis and reporting workflows in uScript.

---
title: "{{analysis_name}} Data Analysis"
type: "data_analysis"
author: "{{author_name}}"
version: "1.0.0"
dataset: "{{dataset_name}}"
---

## 📊 Data Analysis: {{analysis_name}}

```uScript
' {{analysis_name}} - Automated Data Analysis
' Generated from uScript data analysis template

SET analysis_name = "{{analysis_name}}"
SET dataset_name = "{{dataset_name}}"
SET author = "{{author_name}}"
SET analysis_date = TODAY()
SET analysis_id = "analysis-" + analysis_date + "-" + generate_id()

LOG_INFO "Starting data analysis: " + analysis_name
LOG_INFO "Dataset: " + dataset_name

' 1. Initialize Analysis Environment
LOG_INFO "Setting up analysis environment..."
CREATE MISSION analysis_name
SET analysis_dir = "./uMemory/analysis/" + analysis_id
create_directory(analysis_dir)
create_directory(analysis_dir + "/data")
create_directory(analysis_dir + "/reports")
create_directory(analysis_dir + "/visualizations")

' 2. Data Source Validation
LOG_INFO "Validating data sources..."
SET data_sources = [{{#each data_sources}}"{{this}}"{{#unless @last}}, {{/unless}}{{/each}}]
SET valid_sources = 0

FOR EACH source IN data_sources
    IF file_exists(source) THEN
        SET valid_sources = valid_sources + 1
        LOG_INFO "✅ Data source found: " + source
        
        ' Copy to analysis directory
        SET source_filename = get_filename(source)
        copy_file(source, analysis_dir + "/data/" + source_filename)
        
    ELSE
        LOG_ERROR "❌ Data source missing: " + source
        CREATE MOVE analysis_id + "/missing-data" {
            "description": "Missing data source: " + source,
            "status": "blocked",
            "priority": "high",
            "created": NOW()
        }
    END IF
NEXT source

IF valid_sources = 0 THEN
    LOG_ERROR "No valid data sources found - analysis cannot proceed"
    EXIT 1
END IF

LOG_INFO "Found " + valid_sources + "/" + data_sources.length + " data sources"

' 3. Data Preprocessing
LOG_INFO "Starting data preprocessing..."
CREATE MOVE analysis_id + "/preprocessing" {
    "description": "Data cleaning and preprocessing",
    "status": "in-progress",
    "created": NOW()
}

{{#if enable_data_cleaning}}
' Data cleaning operations
LOG_INFO "Performing data cleaning..."
FOR EACH source IN data_sources
    IF file_exists(source) THEN
        SET cleaned_file = analysis_dir + "/data/cleaned-" + get_filename(source)
        
        {{#each cleaning_operations}}
        ' {{this.description}}
        RUN "{{this.command}}" + " " + source + " > " + cleaned_file
        LOG_INFO "Applied cleaning: {{this.description}}"
        {{/each}}
        
        ' Validate cleaned data
        SET record_count = count_records(cleaned_file)
        LOG_INFO "Cleaned data records: " + record_count
        
        IF record_count = 0 THEN
            LOG_WARN "Warning: No records after cleaning " + source
        END IF
    END IF
NEXT source
{{/if}}

' 4. Data Analysis Operations
LOG_INFO "Performing analysis operations..."
CREATE MOVE analysis_id + "/analysis" {
    "description": "Core data analysis and calculations",
    "status": "in-progress", 
    "created": NOW()
}

{{#each analysis_operations}}
' {{this.description}}
LOG_INFO "Running analysis: {{this.description}}"
SET analysis_result = ""

{{#if this.type == "statistics"}}
' Statistical analysis
RUN "{{this.command}}" + " " + analysis_dir + "/data/{{this.input_file}}"
SET analysis_result = capture_output()
{{/if}}

{{#if this.type == "aggregation"}}
' Data aggregation
SET aggregation_query = "{{this.query}}"
SET result_file = analysis_dir + "/reports/{{this.output_file}}"
RUN "{{this.command}}" + " '" + aggregation_query + "' " + analysis_dir + "/data/{{this.input_file}} > " + result_file
SET analysis_result = "Results saved to " + result_file
{{/if}}

{{#if this.type == "visualization"}}
' Generate visualization
SET viz_file = analysis_dir + "/visualizations/{{this.output_file}}"
RUN "{{this.command}}" + " " + analysis_dir + "/data/{{this.input_file}} " + viz_file
SET analysis_result = "Visualization created: " + viz_file
{{/if}}

LOG_INFO "Analysis completed: " + analysis_result
CREATE MOVE analysis_id + "/{{this.id}}" {
    "description": "{{this.description}}",
    "status": "completed",
    "result": analysis_result,
    "created": NOW()
}

{{/each}}

' 5. Generate Summary Report
LOG_INFO "Generating analysis summary report..."
SET report_file = analysis_dir + "/reports/summary-" + analysis_date + ".md"
SET report_content = "# " + analysis_name + " - Analysis Summary\n\n"
SET report_content = report_content + "**Generated:** " + NOW() + "\n"
SET report_content = report_content + "**Author:** " + author + "\n"
SET report_content = report_content + "**Dataset:** " + dataset_name + "\n\n"

' Add data source information
SET report_content = report_content + "## 📊 Data Sources\n\n"
FOR EACH source IN data_sources
    IF file_exists(source) THEN
        SET file_size = get_file_size(source)
        SET record_count = count_records(source)
        SET report_content = report_content + "- **" + get_filename(source) + "** - "
        SET report_content = report_content + record_count + " records (" + file_size + ")\n"
    END IF
NEXT source

' Add analysis results
SET report_content = report_content + "\n## 🔍 Analysis Results\n\n"
{{#each analysis_operations}}
SET report_content = report_content + "### {{this.description}}\n\n"
IF file_exists(analysis_dir + "/reports/{{this.output_file}}") THEN
    SET result_data = read_file(analysis_dir + "/reports/{{this.output_file}}")
    SET report_content = report_content + "```\n" + result_data + "\n```\n\n"
END IF
{{/each}}

' Add recommendations
SET report_content = report_content + "\n## 💡 Recommendations\n\n"
{{#each recommendations}}
SET report_content = report_content + "- {{this}}\n"
{{/each}}

write_file(report_file, report_content)
LOG_INFO "Summary report generated: " + report_file

' 6. Create Visualizations Index
IF count_files(analysis_dir + "/visualizations/*") > 0 THEN
    LOG_INFO "Creating visualizations index..."
    SET viz_index = analysis_dir + "/visualizations/index.md"
    SET viz_content = "# Visualizations - " + analysis_name + "\n\n"
    
    FOR EACH viz_file IN get_files(analysis_dir + "/visualizations/*")
        IF get_filename(viz_file) != "index.md" THEN
            SET viz_content = viz_content + "- [" + get_filename(viz_file) + "](./" + get_filename(viz_file) + ")\n"
        END IF
    NEXT viz_file
    
    write_file(viz_index, viz_content)
END IF

' 7. Performance Metrics
SET analysis_duration = time_diff(NOW(), analysis_start_time)
SET performance_metrics = {
    "analysis_id": analysis_id,
    "duration": analysis_duration,
    "data_sources_processed": valid_sources,
    "reports_generated": count_files(analysis_dir + "/reports/*"),
    "visualizations_created": count_files(analysis_dir + "/visualizations/*"),
    "total_records_processed": get_total_records_processed(),
    "completion_date": NOW()
}

write_json_file(analysis_dir + "/metrics.json", performance_metrics)
LOG_PERFORMANCE "data_analysis", analysis_duration

' 8. Create Analysis Milestone
CREATE MILESTONE analysis_id + "/analysis-complete"
LOG_MILESTONE analysis_id, "analysis-complete"

' 9. Dashboard Update
LOG_INFO "Updating analysis dashboard..."
SET dashboard_entry = {
    "analysis_id": analysis_id,
    "name": analysis_name,
    "status": "completed",
    "dataset": dataset_name,
    "completion_date": NOW(),
    "reports_path": analysis_dir + "/reports/",
    "summary_report": report_file,
    "metrics": performance_metrics
}

write_json_file("./uMemory/dashboard/analyses/" + analysis_id + ".json", dashboard_entry)

' Final Summary
LOG_INFO "Data analysis completed successfully"
LOG_DASHBOARD "📊 Analysis completed: " + analysis_name
LOG_INFO "Results available in: " + analysis_dir

SET completion_summary = {
    "analysis": analysis_name,
    "dataset": dataset_name,
    "duration": analysis_duration,
    "output_directory": analysis_dir,
    "summary_report": report_file,
    "status": "completed"
}

LOG_TO_FILE "./uMemory/logs/analysis-" + analysis_date + ".log",
             "Analysis completed: " + JSON.stringify(completion_summary)
```

## 📋 Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{analysis_name}}` | Analysis project name | "Sales Performance Q3" |
| `{{dataset_name}}` | Primary dataset identifier | "sales_data_q3_2025" |
| `{{author_name}}` | Analysis author | "Data Analyst" |

## 🔧 Configuration Arrays

### Data Sources
```json
{
  "data_sources": [
    "./uMemory/datasets/sales_q3.csv",
    "./uMemory/datasets/customer_data.json"
  ]
}
```

### Analysis Operations
```json
{
  "analysis_operations": [
    {
      "id": "basic-stats",
      "description": "Calculate basic statistics",
      "type": "statistics", 
      "command": "python ./uScript/utils/stats.py",
      "input_file": "cleaned-sales_q3.csv",
      "output_file": "basic_stats.txt"
    }
  ]
}
```

## 🎯 Usage

1. Copy template to new analysis file
2. Configure data sources and operations
3. Customize analysis steps
4. Run script to perform automated analysis

---

*This template provides comprehensive data analysis with automated reporting, visualization, and performance tracking.*
