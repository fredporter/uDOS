# 🛡️ Geographic Data Validation Rules

**Version**: v2.1.0  
**Created**: July 19, 2025  
**Purpose**: Comprehensive validation rules for geographic and timezone data

---

## 📏 Core Validation Rules

### Coordinate Validation
```shortcode
{COORDINATE_VALIDATION}
latitude:
  type: numeric
  required: true
  minimum: -90
  maximum: 90
  precision: 6
  format: decimal_degrees
  pattern: "^-?(?:90(?:\\.0+)?|[1-8]?\\d(?:\\.\\d+)?)$"
  error_messages:
    required: "Latitude is required"
    range: "Latitude must be between -90 and 90 degrees"
    precision: "Latitude precision cannot exceed 6 decimal places"
    
longitude:
  type: numeric
  required: true
  minimum: -180
  maximum: 180
  precision: 6
  format: decimal_degrees
  pattern: "^-?(?:180(?:\\.0+)?|1[0-7]\\d(?:\\.\\d+)?|[1-9]?\\d(?:\\.\\d+)?)$"
  error_messages:
    required: "Longitude is required"
    range: "Longitude must be between -180 and 180 degrees"
    precision: "Longitude precision cannot exceed 6 decimal places"

coordinate_pair_validation:
  - rule: "not_null_island"
    condition: "!(latitude == 0 && longitude == 0)"
    message: "Coordinates cannot be exactly 0,0 (Null Island)"
    
  - rule: "not_impossible_land"
    condition: "validate_against_land_mask(latitude, longitude)"
    message: "Coordinates appear to be in open ocean without known land"
    warning_only: true
    
  - rule: "precision_consistency"
    condition: "decimal_places(latitude) == decimal_places(longitude)"
    message: "Latitude and longitude should have consistent precision"
    warning_only: true
{/COORDINATE_VALIDATION}
```

### Timezone Validation
```shortcode
{TIMEZONE_VALIDATION}
iana_timezone:
  type: string
  required: true
  format: iana_timezone_identifier
  pattern: "^[A-Z][a-z]+/[A-Za-z_]+(?:/[A-Za-z_]+)?$"
  valid_timezones: "{{iana_timezone_list}}"
  case_sensitive: true
  error_messages:
    required: "Timezone is required"
    format: "Must be a valid IANA timezone identifier (e.g., America/New_York)"
    not_found: "Timezone not found in IANA database"
    deprecated: "This timezone identifier is deprecated, use: {{suggested_timezone}}"

utc_offset:
  type: string
  required: true
  format: utc_offset
  pattern: "^[+-](?:0[0-9]|1[0-4]):[0-5][0-9]$"
  valid_offsets: [
    "-12:00", "-11:00", "-10:00", "-09:30", "-09:00", "-08:00", "-07:00",
    "-06:00", "-05:00", "-04:00", "-03:30", "-03:00", "-02:00", "-01:00",
    "+00:00", "+01:00", "+02:00", "+03:00", "+03:30", "+04:00", "+04:30",
    "+05:00", "+05:30", "+05:45", "+06:00", "+06:30", "+07:00", "+08:00",
    "+08:30", "+08:45", "+09:00", "+09:30", "+10:00", "+10:30", "+11:00",
    "+12:00", "+12:45", "+13:00", "+14:00"
  ]
  error_messages:
    required: "UTC offset is required"
    format: "UTC offset must be in format ±HH:MM"
    invalid_range: "UTC offset must be between -12:00 and +14:00"

dst_validation:
  dst_active:
    type: boolean
    default: false
    
  dst_offset:
    type: string
    required_if: "dst_active == true"
    format: utc_offset
    pattern: "^[+-](?:0[0-9]|1[0-4]):[0-5][0-9]$"
    validation_rule: "dst_offset != utc_offset"
    error_messages:
      required_if: "DST offset required when DST is active"
      same_as_standard: "DST offset must be different from standard UTC offset"

timezone_coordinate_consistency:
  - rule: "timezone_matches_location"
    condition: "validate_timezone_for_coordinates(timezone, latitude, longitude)"
    message: "Timezone {{timezone}} is not typically used at coordinates {{latitude}}, {{longitude}}"
    severity: warning
    auto_suggest: true
{/TIMEZONE_VALIDATION}
```

### Location Name Validation
```shortcode
{LOCATION_NAME_VALIDATION}
city_name:
  type: string
  required: true
  min_length: 2
  max_length: 100
  pattern: "^[\\p{L}\\p{M}\\p{N}\\p{Pc}\\p{Pd}\\s]+$"
  unicode_support: true
  trim_whitespace: true
  normalize_unicode: true
  error_messages:
    required: "Location name is required"
    min_length: "Location name must be at least 2 characters"
    max_length: "Location name cannot exceed 100 characters"
    invalid_characters: "Location name contains invalid characters"
    
country_name:
  type: string
  required: true
  valid_countries: "{{iso_3166_country_list}}"
  case_insensitive: true
  alias_support: true
  error_messages:
    required: "Country name is required"
    not_found: "Country not recognized"
    
country_code:
  type: string
  required: true
  format: iso_3166_alpha2
  pattern: "^[A-Z]{2}$"
  valid_codes: "{{iso_3166_alpha2_list}}"
  case_sensitive: true
  error_messages:
    required: "Country code is required"
    format: "Country code must be 2 uppercase letters"
    not_found: "Invalid ISO 3166-1 alpha-2 country code"

state_province:
  type: string
  required: false
  max_length: 100
  pattern: "^[\\p{L}\\p{M}\\p{N}\\p{Pc}\\p{Pd}\\s]+$"
  dependent_validation:
    - country: "US"
      valid_values: "{{us_state_list}}"
    - country: "CA"
      valid_values: "{{canada_province_list}}"
    - country: "AU"
      valid_values: "{{australia_state_list}}"
{/LOCATION_NAME_VALIDATION}
```

### Demographic Validation
```shortcode
{DEMOGRAPHIC_VALIDATION}
population:
  type: integer
  required: false
  minimum: 0
  maximum: 50000000
  validation_rules:
    - rule: "reasonable_for_city_type"
      condition: "validate_population_city_type_consistency(population, city_type)"
      message: "Population {{population}} seems unusual for city type {{city_type}}"
      severity: warning
      
city_type:
  type: string
  required: true
  valid_values:
    - value: "capital"
      label: "Capital City"
      min_population: 50000
      
    - value: "megacity"
      label: "Megacity"
      min_population: 10000000
      
    - value: "major_city"
      label: "Major City"
      min_population: 1000000
      max_population: 10000000
      
    - value: "large_city"
      label: "Large City"
      min_population: 300000
      max_population: 1000000
      
    - value: "medium_city"
      label: "Medium City"
      min_population: 100000
      max_population: 300000
      
    - value: "small_city"
      label: "Small City"
      min_population: 50000
      max_population: 100000
      
    - value: "town"
      label: "Town"
      min_population: 10000
      max_population: 50000
      
    - value: "village"
      label: "Village"
      min_population: 1000
      max_population: 10000
      
    - value: "hamlet"
      label: "Hamlet"
      max_population: 1000
      
  error_messages:
    required: "City type is required"
    invalid_value: "Invalid city type"

elevation:
  type: numeric
  required: false
  minimum: -500
  maximum: 9000
  unit: meters
  validation_rules:
    - rule: "realistic_for_location"
      condition: "validate_elevation_for_coordinates(elevation, latitude, longitude)"
      message: "Elevation {{elevation}}m seems unrealistic for location"
      severity: warning
      tolerance: 100

area_km2:
  type: numeric
  required: false
  minimum: 0.1
  maximum: 100000
  unit: square_kilometers
  precision: 2
{/DEMOGRAPHIC_VALIDATION}
```

### Cultural Data Validation
```shortcode
{CULTURAL_DATA_VALIDATION}
language_codes:
  type: array
  element_type: string
  required: false
  max_items: 10
  element_validation:
    format: iso_639_alpha2
    pattern: "^[a-z]{2}$"
    valid_codes: "{{iso_639_language_list}}"
  error_messages:
    invalid_code: "Invalid ISO 639-1 language code: {{value}}"
    too_many: "Maximum 10 languages allowed"

currency_code:
  type: string
  required: false
  format: iso_4217
  pattern: "^[A-Z]{3}$"
  valid_codes: "{{iso_4217_currency_list}}"
  case_sensitive: true
  error_messages:
    format: "Currency code must be 3 uppercase letters"
    not_found: "Invalid ISO 4217 currency code"

climate_classification:
  type: string
  required: false
  valid_values: [
    "tropical_rainforest",
    "tropical_savanna", 
    "hot_desert",
    "cold_desert",
    "mediterranean",
    "humid_subtropical",
    "humid_continental",
    "oceanic",
    "subarctic",
    "tundra",
    "ice_cap",
    "subtropical_highland",
    "hot_semi_arid"
  ]
  error_messages:
    invalid_value: "Invalid climate classification"

founded_year:
  type: integer
  required: false
  minimum: -3000
  maximum: 2025
  validation_rules:
    - rule: "not_future"
      condition: "founded_year <= current_year"
      message: "Founded year cannot be in the future"
      
    - rule: "reasonable_for_location"
      condition: "validate_founding_year_for_region(founded_year, country_code)"
      message: "Founded year seems unrealistic for this region"
      severity: warning
{/CULTURAL_DATA_VALIDATION}
```

---

## 🔍 Advanced Validation Rules

### Cross-Field Validation
```shortcode
{CROSS_FIELD_VALIDATION}
location_consistency:
  - rule: "country_timezone_match"
    fields: [country_code, timezone_id]
    condition: "timezone_id in get_country_timezones(country_code)"
    message: "Timezone {{timezone_id}} is not typically used in {{country_code}}"
    severity: warning
    auto_suggest: true
    
  - rule: "coordinates_country_match"
    fields: [latitude, longitude, country_code]
    condition: "point_in_country_boundaries(latitude, longitude, country_code)"
    message: "Coordinates appear to be outside {{country_code}} boundaries"
    severity: warning
    
  - rule: "population_area_density"
    fields: [population, area_km2]
    condition: "population/area_km2 < 100000"
    message: "Population density exceeds realistic urban limits"
    severity: warning

temporal_consistency:
  - rule: "dst_period_validation"
    fields: [timezone_id, dst_active]
    condition: "dst_active == has_dst_in_timezone(timezone_id)"
    message: "DST setting inconsistent with timezone rules"
    
  - rule: "seasonal_dst_check"
    fields: [timezone_id, dst_active]
    condition: "dst_active == is_dst_active_now(timezone_id)"
    message: "DST setting may be incorrect for current date"
    severity: info

geographic_consistency:
  - rule: "elevation_climate_match"
    fields: [elevation, climate_classification]
    condition: "validate_elevation_climate_consistency(elevation, climate_classification)"
    message: "Climate classification unusual for elevation {{elevation}}m"
    severity: warning
    
  - rule: "coastal_elevation_check"
    fields: [latitude, longitude, elevation]
    condition: "!is_coastal(latitude, longitude) || elevation >= -10"
    message: "Coastal location with unusual elevation"
    severity: warning
{/CROSS_FIELD_VALIDATION}
```

### Batch Validation Rules
```shortcode
{BATCH_VALIDATION}
duplicate_detection:
  duplicate_criteria:
    - fields: [latitude, longitude]
      tolerance: 0.001
      message: "Duplicate coordinates detected"
      
    - fields: [city_name, country_code]
      case_insensitive: true
      message: "Duplicate city name in same country"
      
    - fields: [timezone_id, coordinates]
      coordinate_tolerance: 0.01
      message: "Very similar locations with same timezone"

consistency_checks:
  global_consistency:
    - rule: "timezone_coverage"
      condition: "all_timezones_represented_in_regions"
      message: "Some major timezones not represented in dataset"
      severity: info
      
    - rule: "population_distribution"
      condition: "validate_global_population_distribution"
      message: "Global population distribution seems skewed"
      severity: warning

data_quality_metrics:
  completeness:
    required_fields_threshold: 0.95
    optional_fields_threshold: 0.80
    
  accuracy:
    coordinate_precision_threshold: 0.99
    timezone_accuracy_threshold: 0.98
    
  consistency:
    cross_field_validation_pass_rate: 0.95
{/BATCH_VALIDATION}
```

### Custom Validation Functions
```shortcode
{CUSTOM_VALIDATION_FUNCTIONS}
geographic_functions:
  validate_timezone_for_coordinates:
    description: "Validates timezone against geographic coordinates"
    parameters: [timezone_id, latitude, longitude]
    returns: boolean
    implementation: "lookup_timezone_boundaries"
    
  point_in_country_boundaries:
    description: "Checks if coordinates fall within country boundaries"
    parameters: [latitude, longitude, country_code]
    returns: boolean
    implementation: "geospatial_boundary_check"
    
  is_coastal:
    description: "Determines if location is coastal"
    parameters: [latitude, longitude]
    returns: boolean
    implementation: "distance_to_coastline < 50km"

temporal_functions:
  has_dst_in_timezone:
    description: "Checks if timezone observes daylight saving time"
    parameters: [timezone_id]
    returns: boolean
    implementation: "iana_dst_rules_lookup"
    
  is_dst_active_now:
    description: "Checks if DST is currently active in timezone"
    parameters: [timezone_id]
    returns: boolean
    implementation: "current_dst_status"

data_quality_functions:
  validate_population_city_type_consistency:
    description: "Validates population against city type"
    parameters: [population, city_type]
    returns: boolean
    implementation: "population_range_check"
    
  validate_elevation_climate_consistency:
    description: "Validates elevation against climate classification"
    parameters: [elevation, climate]
    returns: boolean
    implementation: "elevation_climate_correlation"
{/CUSTOM_VALIDATION_FUNCTIONS}
```

---

## 📊 Validation Error Handling

### Error Classification
```shortcode
{ERROR_CLASSIFICATION}
error_levels:
  critical:
    description: "Data cannot be processed"
    action: "reject_record"
    examples:
      - "Invalid coordinate format"
      - "Missing required fields"
      - "Malformed timezone identifier"
      
  error:
    description: "Data has significant issues"
    action: "flag_for_review"
    examples:
      - "Coordinates outside valid range"
      - "Unknown country code"
      - "Invalid population value"
      
  warning:
    description: "Data seems unusual but processable"
    action: "accept_with_flag"
    examples:
      - "Timezone unusual for location"
      - "High population density"
      - "Elevation seems high for climate"
      
  info:
    description: "Informational notices"
    action: "accept_with_note"
    examples:
      - "Optional field missing"
      - "Precision could be improved"
      - "Alternative name available"

error_reporting:
  format: structured_json
  include_suggestions: true
  include_line_numbers: true
  max_errors_per_record: 10
  
validation_summary:
  total_records: "{{record_count}}"
  passed_validation: "{{passed_count}}"
  failed_validation: "{{failed_count}}"
  warnings_generated: "{{warning_count}}"
  
  error_breakdown:
    critical: "{{critical_count}}"
    error: "{{error_count}}"
    warning: "{{warning_count}}"
    info: "{{info_count}}"
{/ERROR_CLASSIFICATION}
```

---

*These comprehensive validation rules ensure data quality and consistency across all geographic and timezone datasets in the uDOS mapping system.*
