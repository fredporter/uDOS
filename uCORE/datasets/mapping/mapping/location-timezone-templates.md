# 🗺️ Location & Timezone Management Template

**Template Version**: v2.1.0  
**Created**: July 19, 2025  
**Purpose**: Complete location and timezone management system with validation

---

## 🌍 Location Management System

### Core Location Template
```shortcode
{LOCATION_MANAGER}
template_type: location_management
version: "2.1.0"

location_data:
  primary:
    name: "{{location_name|validate:city_name}}"
    coordinates:
      latitude: {{latitude|validate:lat_range|format:decimal_6}}
      longitude: {{longitude|validate:lon_range|format:decimal_6}}
    country: "{{country|validate:iso_country}}"
    country_code: "{{country_code|validate:iso_3166_alpha2}}"
    
  secondary:
    state_province: "{{state_province|optional}}"
    city_type: "{{city_type|select:capital,major_city,city,town,village}}"
    population: {{population|optional|validate:population_range}}
    elevation: {{elevation|optional|validate:elevation_range}}
    founded_year: {{founded_year|optional|validate:year_range}}
    
  timezone:
    iana_id: "{{timezone_id|validate:iana_timezone}}"
    utc_offset: "{{utc_offset|validate:utc_format}}"
    dst_active: {{dst_active|boolean|default:false}}
    dst_offset: "{{dst_offset|conditional:dst_active|validate:utc_format}}"
    
  metadata:
    climate: "{{climate_type|optional|select:climate_options}}"
    languages: [{{language_codes|array:iso_639}}]
    currency: "{{currency_code|validate:iso_4217}}"
    area_km2: {{area_km2|optional|numeric|min:0}}

validation_rules:
  city_name:
    required: true
    min_length: 2
    max_length: 100
    pattern: "^[\\p{L}\\p{M}\\p{N}\\p{Pc}\\p{Pd}\\s]+$"
    
  lat_range:
    min: -90
    max: 90
    precision: 6
    
  lon_range:
    min: -180
    max: 180
    precision: 6
    
  iso_3166_alpha2:
    pattern: "^[A-Z]{2}$"
    
  iana_timezone:
    pattern: "^[A-Z][a-z]+/[A-Za-z_]+(?:/[A-Za-z_]+)?$"
    
  utc_format:
    pattern: "^[+-](?:0[0-9]|1[0-4]):[0-5][0-9]$"
    
  population_range:
    min: 0
    max: 50000000
    
  elevation_range:
    min: -500
    max: 9000
{/LOCATION_MANAGER}
```

### Location Entry Form Template
```shortcode
{LOCATION_ENTRY_FORM}
form_id: "location_entry_v2_1"
title: "Location Registration Form"

sections:
  basic_info:
    title: "Basic Information"
    fields:
      location_name:
        type: text
        label: "Location Name"
        placeholder: "Enter official city or location name"
        required: true
        validation: "{{city_name_validation}}"
        help_text: "Use the official name as recognized by local government"
        
      coordinates:
        type: coordinate_pair
        label: "Geographic Coordinates"
        latitude:
          placeholder: "40.7128"
          step: 0.000001
          min: -90
          max: 90
        longitude:
          placeholder: "-74.0060"
          step: 0.000001
          min: -180
          max: 180
        map_picker: enabled
        required: true
        
      country_selection:
        type: select
        label: "Country"
        options: "{{country_dataset}}"
        searchable: true
        required: true
        on_change: "update_timezone_options"
        
      state_province:
        type: text
        label: "State/Province"
        placeholder: "State, province, or administrative region"
        required: false
        
  classification:
    title: "Location Classification"
    fields:
      city_type:
        type: select
        label: "Location Type"
        options:
          - value: "capital"
            label: "Capital City"
            description: "National or regional capital"
          - value: "megacity"
            label: "Megacity"
            description: "Population > 10 million"
          - value: "major_city"
            label: "Major City"
            description: "Population 1-10 million"
          - value: "large_city"
            label: "Large City"
            description: "Population 300k-1M"
          - value: "medium_city"
            label: "Medium City"
            description: "Population 100k-300k"
          - value: "small_city"
            label: "Small City"
            description: "Population 50k-100k"
          - value: "town"
            label: "Town"
            description: "Population 10k-50k"
          - value: "village"
            label: "Village"
            description: "Population < 10k"
        required: true
        
      population:
        type: number
        label: "Population"
        placeholder: "Current population estimate"
        min: 0
        max: 50000000
        required: false
        help_text: "Latest available population figure"
        
  timezone_info:
    title: "Timezone Information"
    fields:
      timezone_selection:
        type: select
        label: "Timezone"
        options: "{{timezone_dataset_filtered}}"
        searchable: true
        required: true
        dependent_on: country_selection
        help_text: "IANA timezone identifier"
        
      manual_timezone:
        type: text
        label: "Manual Timezone Entry"
        placeholder: "e.g., America/New_York"
        pattern: "^[A-Z][a-z]+/[A-Za-z_]+(?:/[A-Za-z_]+)?$"
        required: false
        show_when: "timezone_selection == 'manual'"
        
  additional_info:
    title: "Additional Information"
    fields:
      elevation:
        type: number
        label: "Elevation (meters)"
        placeholder: "Height above sea level"
        min: -500
        max: 9000
        required: false
        
      founded_year:
        type: number
        label: "Founded Year"
        placeholder: "Year of establishment"
        min: -3000
        max: 2025
        required: false
        
      climate:
        type: select
        label: "Climate Classification"
        options:
          - "tropical_rainforest"
          - "tropical_savanna"
          - "hot_desert"
          - "cold_desert"
          - "mediterranean"
          - "humid_subtropical"
          - "humid_continental"
          - "oceanic"
          - "subarctic"
          - "tundra"
          - "ice_cap"
          - "subtropical_highland"
          - "hot_semi_arid"
        required: false
        
      languages:
        type: multi_select
        label: "Primary Languages"
        options: "{{language_dataset}}"
        searchable: true
        required: false
        
      currency:
        type: select
        label: "Local Currency"
        options: "{{currency_dataset}}"
        searchable: true
        required: false

form_actions:
  validate:
    action: "validate_form_data"
    real_time: true
    
  geocode:
    action: "reverse_geocode_coordinates"
    trigger: "coordinate_change"
    
  timezone_detect:
    action: "detect_timezone_from_coordinates"
    trigger: "coordinate_change"
    
  save:
    action: "save_location_data"
    validation: "full"
    
  cancel:
    action: "cancel_form"
    confirm: true
{/LOCATION_ENTRY_FORM}
```

---

## 🕐 Timezone Management System

### Timezone Converter Template
```shortcode
{TIMEZONE_CONVERTER}
converter_type: "multi_timezone"
version: "2.1.0"

input_section:
  source_datetime:
    type: datetime_local
    label: "Source Date & Time"
    value: "{{input_datetime|default:now}}"
    format: "YYYY-MM-DDTHH:mm:ss"
    required: true
    
  source_timezone:
    type: select
    label: "Source Timezone"
    options: "{{all_timezones_dataset}}"
    searchable: true
    value: "{{default_timezone|detect_from_browser}}"
    required: true

conversion_targets:
  target_timezones:
    type: multi_select
    label: "Convert To Timezones"
    options: "{{all_timezones_dataset}}"
    searchable: true
    max_selections: 10
    popular_timezones:
      - "America/New_York"
      - "Europe/London"
      - "Asia/Tokyo"
      - "Australia/Sydney"
      - "America/Los_Angeles"
      - "Europe/Paris"
      - "Asia/Shanghai"
      - "America/Chicago"
    
conversion_output:
  format_options:
    datetime_format:
      type: select
      label: "Display Format"
      options:
        - value: "12h"
          label: "12-hour (3:30 PM)"
        - value: "24h"
          label: "24-hour (15:30)"
        - value: "iso"
          label: "ISO 8601 (2025-07-19T15:30:00)"
      default: "12h"
      
    show_offset:
      type: checkbox
      label: "Show UTC Offset"
      default: true
      
    show_timezone_name:
      type: checkbox
      label: "Show Timezone Name"
      default: true
      
    show_dst_info:
      type: checkbox
      label: "Show Daylight Saving Info"
      default: true

results_display:
  table_format:
    columns:
      - timezone: "Timezone"
      - local_time: "Local Time"
      - utc_offset: "UTC Offset"
      - dst_status: "DST Status"
      - time_difference: "Difference"
    
  export_options:
    formats: ["csv", "json", "ical"]
    
batch_conversion:
  enabled: true
  file_upload:
    accepted_formats: ["csv", "xlsx", "json"]
    max_file_size: "10MB"
    template_download: true
{/TIMEZONE_CONVERTER}
```

### World Clock Template
```shortcode
{WORLD_CLOCK}
clock_type: "multi_timezone_display"
version: "2.1.0"

default_locations:
  - name: "New York"
    timezone: "America/New_York"
    coordinates: [40.7128, -74.0060]
    
  - name: "London"
    timezone: "Europe/London"
    coordinates: [51.5074, -0.1278]
    
  - name: "Tokyo"
    timezone: "Asia/Tokyo"
    coordinates: [35.6762, 139.6503]
    
  - name: "Sydney"
    timezone: "Australia/Sydney"
    coordinates: [-33.8688, 151.2093]

custom_locations:
  add_location:
    type: "location_search"
    search_dataset: "{{global_cities_dataset}}"
    allow_custom: true
    max_locations: 20
    
  location_manager:
    actions:
      - "add_location"
      - "remove_location"
      - "reorder_locations"
      - "set_primary_location"

display_options:
  clock_format:
    type: select
    options:
      - value: "analog"
        label: "Analog Clock"
      - value: "digital"
        label: "Digital Display"
      - value: "both"
        label: "Analog + Digital"
    default: "digital"
    
  time_format:
    type: select
    options:
      - value: "12h"
        label: "12-hour"
      - value: "24h"
        label: "24-hour"
    default: "12h"
    
  show_seconds:
    type: checkbox
    default: true
    
  show_date:
    type: checkbox
    default: true
    
  show_timezone_name:
    type: checkbox
    default: true
    
  show_utc_offset:
    type: checkbox
    default: true
    
  auto_refresh:
    type: checkbox
    default: true
    interval: 1000

layout_options:
  grid_columns:
    type: select
    options: [1, 2, 3, 4, 6]
    default: 3
    
  compact_mode:
    type: checkbox
    default: false
    
  theme:
    type: select
    options:
      - "light"
      - "dark"
      - "auto"
    default: "auto"
{/WORLD_CLOCK}
```

---

## 📍 Location Search & Discovery

### Advanced Location Search
```shortcode
{LOCATION_SEARCH_ADVANCED}
search_interface: "comprehensive"
version: "2.1.0"

search_criteria:
  text_search:
    type: text
    label: "Search Locations"
    placeholder: "Enter city, country, or region name"
    autocomplete: true
    min_length: 2
    search_fields: ["name", "aliases", "country", "state_province"]
    
  geographic_filter:
    proximity_search:
      enabled: true
      center_point:
        type: coordinate_picker
        label: "Search Center"
        map_interface: true
        
      radius:
        type: range_slider
        label: "Search Radius (km)"
        min: 1
        max: 20000
        default: 100
        scale: "logarithmic"
        
    bounding_box:
      enabled: true
      northeast: [{{ne_lat}}, {{ne_lon}}]
      southwest: [{{sw_lat}}, {{sw_lon}}]
      
  demographic_filter:
    population_range:
      type: dual_range_slider
      label: "Population Range"
      min: 0
      max: 50000000
      default_min: 10000
      default_max: 10000000
      scale: "logarithmic"
      
    city_types:
      type: checkbox_group
      label: "Location Types"
      options:
        - value: "capital"
          label: "Capital Cities"
        - value: "megacity"
          label: "Megacities (>10M)"
        - value: "major_city"
          label: "Major Cities (1-10M)"
        - value: "large_city"
          label: "Large Cities (300k-1M)"
        - value: "medium_city"
          label: "Medium Cities (100k-300k)"
        - value: "small_city"
          label: "Small Cities (50k-100k)"
        - value: "town"
          label: "Towns (10k-50k)"
        - value: "village"
          label: "Villages (<10k)"
      allow_multiple: true
      
  geographic_filter:
    countries:
      type: multi_select
      label: "Countries"
      options: "{{country_dataset}}"
      searchable: true
      grouping: "by_continent"
      
    continents:
      type: checkbox_group
      label: "Continents"
      options:
        - "Africa"
        - "Antarctica"
        - "Asia"
        - "Europe"
        - "North America"
        - "Oceania"
        - "South America"
        
    timezones:
      type: multi_select
      label: "Timezones"
      options: "{{timezone_dataset}}"
      searchable: true
      grouping: "by_region"

search_results:
  display_format:
    type: select
    options:
      - value: "list"
        label: "List View"
      - value: "grid"
        label: "Grid View"
      - value: "map"
        label: "Map View"
      - value: "table"
        label: "Table View"
    default: "list"
    
  sorting_options:
    field:
      type: select
      options:
        - value: "relevance"
          label: "Relevance"
        - value: "name"
          label: "Name (A-Z)"
        - value: "population"
          label: "Population"
        - value: "distance"
          label: "Distance"
        - value: "elevation"
          label: "Elevation"
      default: "relevance"
      
    order:
      type: select
      options:
        - value: "asc"
          label: "Ascending"
        - value: "desc"
          label: "Descending"
      default: "desc"
      
  pagination:
    results_per_page:
      type: select
      options: [10, 20, 50, 100]
      default: 20
      
    infinite_scroll:
      type: checkbox
      default: false

result_actions:
  individual_actions:
    - "view_details"
    - "add_to_favorites"
    - "convert_timezone"
    - "get_directions"
    - "export_data"
    
  batch_actions:
    - "export_selected"
    - "add_to_collection"
    - "compare_locations"
    - "generate_report"
{/LOCATION_SEARCH_ADVANCED}
```

---

## 🗃️ Data Management Templates

### Location Data Export
```shortcode
{LOCATION_DATA_EXPORT}
export_type: "location_dataset"
version: "2.1.0"

export_options:
  format_selection:
    type: radio_group
    label: "Export Format"
    options:
      - value: "csv"
        label: "CSV (Comma-separated values)"
        description: "Best for spreadsheet applications"
        
      - value: "json"
        label: "JSON (JavaScript Object Notation)"
        description: "Best for web applications"
        
      - value: "xlsx"
        label: "Excel Spreadsheet"
        description: "Best for Microsoft Excel"
        
      - value: "geojson"
        label: "GeoJSON"
        description: "Best for mapping applications"
        
      - value: "kml"
        label: "KML (Google Earth)"
        description: "Best for Google Earth"
    default: "csv"
    
  field_selection:
    type: checkbox_group
    label: "Include Fields"
    options:
      - value: "basic_info"
        label: "Basic Information"
        description: "Name, coordinates, country"
        default: true
        
      - value: "timezone_data"
        label: "Timezone Data"
        description: "Timezone ID, UTC offset, DST info"
        default: true
        
      - value: "demographic_data"
        label: "Demographic Data"
        description: "Population, area, density"
        default: true
        
      - value: "geographic_data"
        label: "Geographic Data"
        description: "Elevation, climate, region"
        default: false
        
      - value: "cultural_data"
        label: "Cultural Data"
        description: "Languages, currency, founding year"
        default: false
        
      - value: "metadata"
        label: "Metadata"
        description: "Data source, last updated, confidence"
        default: false

export_filters:
  location_filter:
    selected_locations: "{{selected_location_ids}}"
    filter_criteria: "{{current_search_filters}}"
    
  date_range:
    type: date_range_picker
    label: "Data Date Range"
    start_date: "{{export_start_date}}"
    end_date: "{{export_end_date}}"
    
export_settings:
  filename:
    type: text
    label: "Filename"
    value: "location_data_{{timestamp}}"
    pattern: "^[a-zA-Z0-9_-]+$"
    
  compression:
    type: checkbox
    label: "Compress File (ZIP)"
    default: false
    
  email_delivery:
    type: checkbox
    label: "Email Export File"
    default: false
    
    email_options:
      recipient:
        type: email
        label: "Email Address"
        required_if: "email_delivery"
        
      message:
        type: textarea
        label: "Message"
        placeholder: "Optional message with the export"
{/LOCATION_DATA_EXPORT}
```

### Data Import Template
```shortcode
{LOCATION_DATA_IMPORT}
import_type: "bulk_location_import"
version: "2.1.0"

import_source:
  source_type:
    type: radio_group
    label: "Import Source"
    options:
      - value: "file_upload"
        label: "Upload File"
        description: "Upload CSV, Excel, or JSON file"
        
      - value: "url_import"
        label: "Import from URL"
        description: "Import from web URL"
        
      - value: "api_import"
        label: "API Import"
        description: "Import from external API"
        
      - value: "manual_entry"
        label: "Manual Entry"
        description: "Enter data manually"
    default: "file_upload"

file_upload_options:
  accepted_formats:
    - "text/csv"
    - "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    - "application/json"
    - "application/geo+json"
  max_file_size: "50MB"
  encoding: "UTF-8"
  
  field_mapping:
    automatic_detection: true
    manual_mapping:
      required_fields:
        - field: "location_name"
          label: "Location Name"
          required: true
          
        - field: "latitude"
          label: "Latitude"
          required: true
          validation: "numeric|-90,90"
          
        - field: "longitude"
          label: "Longitude"
          required: true
          validation: "numeric|-180,180"
          
        - field: "country_code"
          label: "Country Code"
          required: true
          validation: "iso_3166_alpha2"
          
        - field: "timezone"
          label: "Timezone"
          required: true
          validation: "iana_timezone"
          
      optional_fields:
        - field: "population"
          label: "Population"
          validation: "numeric|0,50000000"
          
        - field: "elevation"
          label: "Elevation"
          validation: "numeric|-500,9000"
          
        - field: "state_province"
          label: "State/Province"
          validation: "string|max:100"

validation_settings:
  strict_validation:
    type: checkbox
    label: "Strict Validation"
    description: "Reject rows with any validation errors"
    default: true
    
  duplicate_handling:
    type: select
    label: "Handle Duplicates"
    options:
      - value: "skip"
        label: "Skip Duplicates"
      - value: "overwrite"
        label: "Overwrite Existing"
      - value: "create_new"
        label: "Create New Entry"
    default: "skip"
    
  error_reporting:
    type: checkbox
    label: "Generate Error Report"
    default: true
    
  max_errors:
    type: number
    label: "Maximum Errors"
    min: 1
    max: 1000
    default: 100

import_preview:
  show_preview: true
  preview_rows: 10
  validation_summary: true
  
import_actions:
  dry_run:
    enabled: true
    description: "Test import without saving data"
    
  batch_size:
    type: number
    label: "Batch Size"
    min: 10
    max: 1000
    default: 100
    description: "Number of records to process at once"
{/LOCATION_DATA_IMPORT}
```

---

*This comprehensive template system provides complete location and timezone management capabilities with robust validation, search, and data management features for the uDOS platform.*
