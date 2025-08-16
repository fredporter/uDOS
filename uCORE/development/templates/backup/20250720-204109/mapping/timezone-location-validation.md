# 🕐 Timezone & Location Validation Template

**Template Version**: v2.1.0  
**Created**: July 19, 2025  
**Purpose**: Comprehensive timezone and location data validation system

---

## 🌍 Location Data Capture Template

### Basic Location Information
```shortcode
{LOCATION_CAPTURE}
location_name: {{location_name|required|string|min:2|max:100}}
coordinates:
  latitude: {{latitude|required|numeric|range:-90,90|precision:6}}
  longitude: {{longitude|required|numeric|range:-180,180|precision:6}}
  
country: {{country|required|select:countries_list}}
country_code: {{country_code|required|format:iso_3166_alpha2}}
state_province: {{state_province|optional|string|max:100}}
city_type: {{city_type|required|select:capital,major_city,city,town,village}}

validation:
  coordinate_precision: 6_decimal_places
  name_format: unicode_letters_numbers_spaces_hyphens
  required_fields: [location_name, coordinates, country, timezone]
{/LOCATION_CAPTURE}
```

### Timezone Validation
```shortcode
{TIMEZONE_VALIDATION}
timezone_id: {{timezone_id|required|format:iana_timezone}}
utc_offset: {{utc_offset|required|format:utc_offset}}
dst_active: {{dst_active|boolean|default:false}}
dst_offset: {{dst_offset|conditional:dst_active|format:utc_offset}}

validation_rules:
  timezone_format: "Continent/City or Area/Location"
  offset_format: "[+-]HH:MM"
  iana_compliance: strict
  
examples:
  valid_timezones:
    - "America/New_York"
    - "Europe/London"
    - "Asia/Tokyo"
    - "Australia/Sydney"
  
  valid_offsets:
    - "+00:00"  # UTC
    - "-05:00"  # EST
    - "+09:00"  # JST
    - "+05:30"  # IST (half-hour offset)
    - "+09:30"  # ACST (half-hour offset)
    - "+05:45"  # NPT (quarter-hour offset)
{/TIMEZONE_VALIDATION}
```

---

## 📊 Data Validation Templates

### Country Selection Template
```shortcode
{COUNTRY_SELECT}
validation_type: iso_3166_alpha2
options: [
  {code: "AD", name: "Andorra", continent: "Europe"},
  {code: "AE", name: "United Arab Emirates", continent: "Asia"},
  {code: "AF", name: "Afghanistan", continent: "Asia"},
  {code: "AG", name: "Antigua and Barbuda", continent: "North America"},
  {code: "AI", name: "Anguilla", continent: "North America"},
  {code: "AL", name: "Albania", continent: "Europe"},
  {code: "AM", name: "Armenia", continent: "Asia"},
  {code: "AO", name: "Angola", continent: "Africa"},
  {code: "AQ", name: "Antarctica", continent: "Antarctica"},
  {code: "AR", name: "Argentina", continent: "South America"},
  {code: "AS", name: "American Samoa", continent: "Oceania"},
  {code: "AT", name: "Austria", continent: "Europe"},
  {code: "AU", name: "Australia", continent: "Oceania"},
  {code: "AW", name: "Aruba", continent: "North America"},
  {code: "AX", name: "Åland Islands", continent: "Europe"},
  {code: "AZ", name: "Azerbaijan", continent: "Asia"},
  {code: "BA", name: "Bosnia and Herzegovina", continent: "Europe"},
  {code: "BB", name: "Barbados", continent: "North America"},
  {code: "BD", name: "Bangladesh", continent: "Asia"},
  {code: "BE", name: "Belgium", continent: "Europe"},
  {code: "BF", name: "Burkina Faso", continent: "Africa"},
  {code: "BG", name: "Bulgaria", continent: "Europe"},
  {code: "BH", name: "Bahrain", continent: "Asia"},
  {code: "BI", name: "Burundi", continent: "Africa"},
  {code: "BJ", name: "Benin", continent: "Africa"},
  {code: "BL", name: "Saint Barthélemy", continent: "North America"},
  {code: "BM", name: "Bermuda", continent: "North America"},
  {code: "BN", name: "Brunei", continent: "Asia"},
  {code: "BO", name: "Bolivia", continent: "South America"},
  {code: "BQ", name: "Caribbean Netherlands", continent: "North America"},
  {code: "BR", name: "Brazil", continent: "South America"},
  {code: "BS", name: "Bahamas", continent: "North America"},
  {code: "BT", name: "Bhutan", continent: "Asia"},
  {code: "BV", name: "Bouvet Island", continent: "Antarctica"},
  {code: "BW", name: "Botswana", continent: "Africa"},
  {code: "BY", name: "Belarus", continent: "Europe"},
  {code: "BZ", name: "Belize", continent: "North America"},
  {code: "CA", name: "Canada", continent: "North America"},
  {code: "CC", name: "Cocos Islands", continent: "Asia"},
  {code: "CD", name: "Democratic Republic of the Congo", continent: "Africa"},
  {code: "CF", name: "Central African Republic", continent: "Africa"},
  {code: "CG", name: "Republic of the Congo", continent: "Africa"},
  {code: "CH", name: "Switzerland", continent: "Europe"},
  {code: "CI", name: "Côte d'Ivoire", continent: "Africa"},
  {code: "CK", name: "Cook Islands", continent: "Oceania"},
  {code: "CL", name: "Chile", continent: "South America"},
  {code: "CM", name: "Cameroon", continent: "Africa"},
  {code: "CN", name: "China", continent: "Asia"},
  {code: "CO", name: "Colombia", continent: "South America"},
  {code: "CR", name: "Costa Rica", continent: "North America"},
  {code: "CU", name: "Cuba", continent: "North America"},
  {code: "CV", name: "Cape Verde", continent: "Africa"},
  {code: "CW", name: "Curaçao", continent: "North America"},
  {code: "CX", name: "Christmas Island", continent: "Asia"},
  {code: "CY", name: "Cyprus", continent: "Asia"},
  {code: "CZ", name: "Czech Republic", continent: "Europe"},
  {code: "DE", name: "Germany", continent: "Europe"},
  {code: "DJ", name: "Djibouti", continent: "Africa"},
  {code: "DK", name: "Denmark", continent: "Europe"},
  {code: "DM", name: "Dominica", continent: "North America"},
  {code: "DO", name: "Dominican Republic", continent: "North America"},
  {code: "DZ", name: "Algeria", continent: "Africa"},
  {code: "EC", name: "Ecuador", continent: "South America"},
  {code: "EE", name: "Estonia", continent: "Europe"},
  {code: "EG", name: "Egypt", continent: "Africa"},
  {code: "EH", name: "Western Sahara", continent: "Africa"},
  {code: "ER", name: "Eritrea", continent: "Africa"},
  {code: "ES", name: "Spain", continent: "Europe"},
  {code: "ET", name: "Ethiopia", continent: "Africa"},
  {code: "FI", name: "Finland", continent: "Europe"},
  {code: "FJ", name: "Fiji", continent: "Oceania"},
  {code: "FK", name: "Falkland Islands", continent: "South America"},
  {code: "FM", name: "Micronesia", continent: "Oceania"},
  {code: "FO", name: "Faroe Islands", continent: "Europe"},
  {code: "FR", name: "France", continent: "Europe"},
  {code: "GA", name: "Gabon", continent: "Africa"},
  {code: "GB", name: "United Kingdom", continent: "Europe"},
  {code: "GD", name: "Grenada", continent: "North America"},
  {code: "GE", name: "Georgia", continent: "Asia"},
  {code: "GF", name: "French Guiana", continent: "South America"},
  {code: "GG", name: "Guernsey", continent: "Europe"},
  {code: "GH", name: "Ghana", continent: "Africa"},
  {code: "GI", name: "Gibraltar", continent: "Europe"},
  {code: "GL", name: "Greenland", continent: "North America"},
  {code: "GM", name: "Gambia", continent: "Africa"},
  {code: "GN", name: "Guinea", continent: "Africa"},
  {code: "GP", name: "Guadeloupe", continent: "North America"},
  {code: "GQ", name: "Equatorial Guinea", continent: "Africa"},
  {code: "GR", name: "Greece", continent: "Europe"},
  {code: "GS", name: "South Georgia", continent: "Antarctica"},
  {code: "GT", name: "Guatemala", continent: "North America"},
  {code: "GU", name: "Guam", continent: "Oceania"},
  {code: "GW", name: "Guinea-Bissau", continent: "Africa"},
  {code: "GY", name: "Guyana", continent: "South America"},
  {code: "HK", name: "Hong Kong", continent: "Asia"},
  {code: "HM", name: "Heard Island and McDonald Islands", continent: "Antarctica"},
  {code: "HN", name: "Honduras", continent: "North America"},
  {code: "HR", name: "Croatia", continent: "Europe"},
  {code: "HT", name: "Haiti", continent: "North America"},
  {code: "HU", name: "Hungary", continent: "Europe"},
  {code: "ID", name: "Indonesia", continent: "Asia"},
  {code: "IE", name: "Ireland", continent: "Europe"},
  {code: "IL", name: "Israel", continent: "Asia"},
  {code: "IM", name: "Isle of Man", continent: "Europe"},
  {code: "IN", name: "India", continent: "Asia"},
  {code: "IO", name: "British Indian Ocean Territory", continent: "Asia"},
  {code: "IQ", name: "Iraq", continent: "Asia"},
  {code: "IR", name: "Iran", continent: "Asia"},
  {code: "IS", name: "Iceland", continent: "Europe"},
  {code: "IT", name: "Italy", continent: "Europe"},
  {code: "JE", name: "Jersey", continent: "Europe"},
  {code: "JM", name: "Jamaica", continent: "North America"},
  {code: "JO", name: "Jordan", continent: "Asia"},
  {code: "JP", name: "Japan", continent: "Asia"},
  {code: "KE", name: "Kenya", continent: "Africa"},
  {code: "KG", name: "Kyrgyzstan", continent: "Asia"},
  {code: "KH", name: "Cambodia", continent: "Asia"},
  {code: "KI", name: "Kiribati", continent: "Oceania"},
  {code: "KM", name: "Comoros", continent: "Africa"},
  {code: "KN", name: "Saint Kitts and Nevis", continent: "North America"},
  {code: "KP", name: "North Korea", continent: "Asia"},
  {code: "KR", name: "South Korea", continent: "Asia"},
  {code: "KW", name: "Kuwait", continent: "Asia"},
  {code: "KY", name: "Cayman Islands", continent: "North America"},
  {code: "KZ", name: "Kazakhstan", continent: "Asia"},
  {code: "LA", name: "Laos", continent: "Asia"},
  {code: "LB", name: "Lebanon", continent: "Asia"},
  {code: "LC", name: "Saint Lucia", continent: "North America"},
  {code: "LI", name: "Liechtenstein", continent: "Europe"},
  {code: "LK", name: "Sri Lanka", continent: "Asia"},
  {code: "LR", name: "Liberia", continent: "Africa"},
  {code: "LS", name: "Lesotho", continent: "Africa"},
  {code: "LT", name: "Lithuania", continent: "Europe"},
  {code: "LU", name: "Luxembourg", continent: "Europe"},
  {code: "LV", name: "Latvia", continent: "Europe"},
  {code: "LY", name: "Libya", continent: "Africa"},
  {code: "MA", name: "Morocco", continent: "Africa"},
  {code: "MC", name: "Monaco", continent: "Europe"},
  {code: "MD", name: "Moldova", continent: "Europe"},
  {code: "ME", name: "Montenegro", continent: "Europe"},
  {code: "MF", name: "Saint Martin", continent: "North America"},
  {code: "MG", name: "Madagascar", continent: "Africa"},
  {code: "MH", name: "Marshall Islands", continent: "Oceania"},
  {code: "MK", name: "North Macedonia", continent: "Europe"},
  {code: "ML", name: "Mali", continent: "Africa"},
  {code: "MM", name: "Myanmar", continent: "Asia"},
  {code: "MN", name: "Mongolia", continent: "Asia"},
  {code: "MO", name: "Macao", continent: "Asia"},
  {code: "MP", name: "Northern Mariana Islands", continent: "Oceania"},
  {code: "MQ", name: "Martinique", continent: "North America"},
  {code: "MR", name: "Mauritania", continent: "Africa"},
  {code: "MS", name: "Montserrat", continent: "North America"},
  {code: "MT", name: "Malta", continent: "Europe"},
  {code: "MU", name: "Mauritius", continent: "Africa"},
  {code: "MV", name: "Maldives", continent: "Asia"},
  {code: "MW", name: "Malawi", continent: "Africa"},
  {code: "MX", name: "Mexico", continent: "North America"},
  {code: "MY", name: "Malaysia", continent: "Asia"},
  {code: "MZ", name: "Mozambique", continent: "Africa"},
  {code: "NA", name: "Namibia", continent: "Africa"},
  {code: "NC", name: "New Caledonia", continent: "Oceania"},
  {code: "NE", name: "Niger", continent: "Africa"},
  {code: "NF", name: "Norfolk Island", continent: "Oceania"},
  {code: "NG", name: "Nigeria", continent: "Africa"},
  {code: "NI", name: "Nicaragua", continent: "North America"},
  {code: "NL", name: "Netherlands", continent: "Europe"},
  {code: "NO", name: "Norway", continent: "Europe"},
  {code: "NP", name: "Nepal", continent: "Asia"},
  {code: "NR", name: "Nauru", continent: "Oceania"},
  {code: "NU", name: "Niue", continent: "Oceania"},
  {code: "NZ", name: "New Zealand", continent: "Oceania"},
  {code: "OM", name: "Oman", continent: "Asia"},
  {code: "PA", name: "Panama", continent: "North America"},
  {code: "PE", name: "Peru", continent: "South America"},
  {code: "PF", name: "French Polynesia", continent: "Oceania"},
  {code: "PG", name: "Papua New Guinea", continent: "Oceania"},
  {code: "PH", name: "Philippines", continent: "Asia"},
  {code: "PK", name: "Pakistan", continent: "Asia"},
  {code: "PL", name: "Poland", continent: "Europe"},
  {code: "PM", name: "Saint Pierre and Miquelon", continent: "North America"},
  {code: "PN", name: "Pitcairn", continent: "Oceania"},
  {code: "PR", name: "Puerto Rico", continent: "North America"},
  {code: "PS", name: "Palestine", continent: "Asia"},
  {code: "PT", name: "Portugal", continent: "Europe"},
  {code: "PW", name: "Palau", continent: "Oceania"},
  {code: "PY", name: "Paraguay", continent: "South America"},
  {code: "QA", name: "Qatar", continent: "Asia"},
  {code: "RE", name: "Réunion", continent: "Africa"},
  {code: "RO", name: "Romania", continent: "Europe"},
  {code: "RS", name: "Serbia", continent: "Europe"},
  {code: "RU", name: "Russia", continent: "Europe"},
  {code: "RW", name: "Rwanda", continent: "Africa"},
  {code: "SA", name: "Saudi Arabia", continent: "Asia"},
  {code: "SB", name: "Solomon Islands", continent: "Oceania"},
  {code: "SC", name: "Seychelles", continent: "Africa"},
  {code: "SD", name: "Sudan", continent: "Africa"},
  {code: "SE", name: "Sweden", continent: "Europe"},
  {code: "SG", name: "Singapore", continent: "Asia"},
  {code: "SH", name: "Saint Helena", continent: "Africa"},
  {code: "SI", name: "Slovenia", continent: "Europe"},
  {code: "SJ", name: "Svalbard and Jan Mayen", continent: "Europe"},
  {code: "SK", name: "Slovakia", continent: "Europe"},
  {code: "SL", name: "Sierra Leone", continent: "Africa"},
  {code: "SM", name: "San Marino", continent: "Europe"},
  {code: "SN", name: "Senegal", continent: "Africa"},
  {code: "SO", name: "Somalia", continent: "Africa"},
  {code: "SR", name: "Suriname", continent: "South America"},
  {code: "SS", name: "South Sudan", continent: "Africa"},
  {code: "ST", name: "São Tomé and Príncipe", continent: "Africa"},
  {code: "SV", name: "El Salvador", continent: "North America"},
  {code: "SX", name: "Sint Maarten", continent: "North America"},
  {code: "SY", name: "Syria", continent: "Asia"},
  {code: "SZ", name: "Eswatini", continent: "Africa"},
  {code: "TC", name: "Turks and Caicos Islands", continent: "North America"},
  {code: "TD", name: "Chad", continent: "Africa"},
  {code: "TF", name: "French Southern Territories", continent: "Antarctica"},
  {code: "TG", name: "Togo", continent: "Africa"},
  {code: "TH", name: "Thailand", continent: "Asia"},
  {code: "TJ", name: "Tajikistan", continent: "Asia"},
  {code: "TK", name: "Tokelau", continent: "Oceania"},
  {code: "TL", name: "East Timor", continent: "Asia"},
  {code: "TM", name: "Turkmenistan", continent: "Asia"},
  {code: "TN", name: "Tunisia", continent: "Africa"},
  {code: "TO", name: "Tonga", continent: "Oceania"},
  {code: "TR", name: "Turkey", continent: "Asia"},
  {code: "TT", name: "Trinidad and Tobago", continent: "North America"},
  {code: "TV", name: "Tuvalu", continent: "Oceania"},
  {code: "TW", name: "Taiwan", continent: "Asia"},
  {code: "TZ", name: "Tanzania", continent: "Africa"},
  {code: "UA", name: "Ukraine", continent: "Europe"},
  {code: "UG", name: "Uganda", continent: "Africa"},
  {code: "UM", name: "United States Minor Outlying Islands", continent: "Oceania"},
  {code: "US", name: "United States", continent: "North America"},
  {code: "UY", name: "Uruguay", continent: "South America"},
  {code: "UZ", name: "Uzbekistan", continent: "Asia"},
  {code: "VA", name: "Vatican City", continent: "Europe"},
  {code: "VC", name: "Saint Vincent and the Grenadines", continent: "North America"},
  {code: "VE", name: "Venezuela", continent: "South America"},
  {code: "VG", name: "British Virgin Islands", continent: "North America"},
  {code: "VI", name: "U.S. Virgin Islands", continent: "North America"},
  {code: "VN", name: "Vietnam", continent: "Asia"},
  {code: "VU", name: "Vanuatu", continent: "Oceania"},
  {code: "WF", name: "Wallis and Futuna", continent: "Oceania"},
  {code: "WS", name: "Samoa", continent: "Oceania"},
  {code: "YE", name: "Yemen", continent: "Asia"},
  {code: "YT", name: "Mayotte", continent: "Africa"},
  {code: "ZA", name: "South Africa", continent: "Africa"},
  {code: "ZM", name: "Zambia", continent: "Africa"},
  {code: "ZW", name: "Zimbabwe", continent: "Africa"}
]

grouping:
  by_continent: true
  alphabetical: true
  most_common_first: [US, GB, CA, AU, DE, FR, JP, CN, IN, BR]
{/COUNTRY_SELECT}
```

### City Type Classification
```shortcode
{CITY_TYPE_SELECT}
options: [
  {value: "capital", label: "Capital City", description: "National or regional capital"},
  {value: "megacity", label: "Megacity", description: "Population > 10 million"},
  {value: "major_city", label: "Major City", description: "Population 1-10 million"},
  {value: "large_city", label: "Large City", description: "Population 300k-1M"},
  {value: "medium_city", label: "Medium City", description: "Population 100k-300k"},
  {value: "small_city", label: "Small City", description: "Population 50k-100k"},
  {value: "town", label: "Town", description: "Population 10k-50k"},
  {value: "small_town", label: "Small Town", description: "Population 1k-10k"},
  {value: "village", label: "Village", description: "Population < 1k"},
  {value: "hamlet", label: "Hamlet", description: "Very small settlement"}
]

validation:
  required: true
  default: "city"
{/CITY_TYPE_SELECT}
```

---

## 🔍 Advanced Search Templates

### Location Search Interface
```shortcode
{LOCATION_SEARCH}
search_criteria:
  text_search: {{search_query|optional|string}}
  coordinates:
    center: [{{center_lat}}, {{center_lon}}]
    radius: {{radius_km|optional|numeric|min:1|max:20000}}
  
  country_filter: {{country_codes|optional|array:iso_codes}}
  timezone_filter: {{timezone_ids|optional|array:iana_timezones}}
  population_range:
    min: {{min_population|optional|numeric|min:0}}
    max: {{max_population|optional|numeric|max:50000000}}
  
  city_types: {{city_types|optional|array:city_type_values}}

sorting:
  by: {{sort_field|select:name,population,distance,timezone}}
  order: {{sort_order|select:asc,desc|default:asc}}
  
pagination:
  page: {{page_number|optional|numeric|min:1|default:1}}
  limit: {{results_per_page|optional|numeric|min:1|max:100|default:20}}
{/LOCATION_SEARCH}
```

### Timezone Conversion Interface
```shortcode
{TIMEZONE_CONVERTER}
source_timezone: {{from_timezone|required|format:iana_timezone}}
target_timezone: {{to_timezone|required|format:iana_timezone}}
datetime_input: {{input_datetime|required|format:iso_8601}}

conversion_result:
  source_time: "{{converted_source_time}}"
  target_time: "{{converted_target_time}}"
  time_difference: "{{time_difference_hours}}"
  dst_note: "{{dst_status_message}}"

batch_conversion:
  enabled: {{enable_batch|boolean|default:false}}
  target_timezones: {{target_timezone_list|conditional:enable_batch|array:iana_timezones}}
{/TIMEZONE_CONVERTER}
```

---

## ⚡ Real-time Validation Rules

### Coordinate Validation
```ascii
                    COORDINATE VALIDATION SYSTEM
    
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                    LATITUDE VALIDATION                            ║
    ║  Range: -90.000000 to +90.000000                                  ║
    ║  ┌─────────────────────────────────────────────────────────────┐  ║
    ║  │  +90° ──── North Pole                                       │  ║
    ║  │   │                                                         │  ║
    ║  │   │   ▲ Northern Hemisphere (Positive Values)               │  ║
    ║  │   │   │                                                     │  ║
    ║  │   0° ──── Equator ──────────────────────────────────────────│  ║
    ║  │   │   │                                                     │  ║
    ║  │   │   ▼ Southern Hemisphere (Negative Values)               │  ║
    ║  │   │                                                         │  ║
    ║  │  -90° ──── South Pole                                       │  ║
    ║  └─────────────────────────────────────────────────────────────┘  ║
    ║                                                                   ║
    ║                   LONGITUDE VALIDATION                            ║
    ║  Range: -180.000000 to +180.000000                                ║
    ║  ┌─────────────────────────────────────────────────────────────┐  ║
    ║  │ -180° ──── International Date Line (West)                   │  ║
    ║  │   │                                                         │  ║
    ║  │   │   ◄── Western Hemisphere (Negative Values)              │  ║
    ║  │   │                                                         │  ║
    ║  │   0° ──── Prime Meridian (Greenwich)                        │  ║
    ║  │   │                                                         │  ║
    ║  │   │   ──► Eastern Hemisphere (Positive Values)              │  ║
    ║  │   │                                                         │  ║
    ║  │ +180° ──── International Date Line (East)                   │  ║
    ║  └─────────────────────────────────────────────────────────────┘  ║
    ╚═══════════════════════════════════════════════════════════════════╝
```

### Timezone Format Validation
```shortcode
{TIMEZONE_FORMAT_RULES}
iana_timezone_pattern: "^[A-Z][a-z]+/[A-Za-z_]+(?:/[A-Za-z_]+)?$"
utc_offset_pattern: "^[+-](?:0[0-9]|1[0-4]):[0-5][0-9]$"

validation_examples:
  valid_timezones:
    - "America/New_York"      # Standard format
    - "Europe/London"         # Standard format
    - "Asia/Kolkata"          # Standard format
    - "Australia/Lord_Howe"   # With underscore
    - "America/North_Dakota/Center"  # Three parts
    
  invalid_timezones:
    - "EST"                   # Abbreviation not allowed
    - "GMT+5"                 # Offset format not allowed
    - "america/new_york"      # Wrong capitalization
    - "New York"              # Spaces not allowed
    - "US/Eastern"            # Deprecated format

  valid_utc_offsets:
    - "+00:00"                # UTC
    - "-05:00"                # EST
    - "+09:30"                # Half-hour offset
    - "+05:45"                # Quarter-hour offset
    - "-03:30"                # Negative half-hour
    
  invalid_utc_offsets:
    - "+5"                    # Missing leading zero
    - "+05"                   # Missing minutes
    - "+25:00"                # Invalid hour
    - "+05:70"                # Invalid minutes
    - "5:00"                  # Missing sign
{/TIMEZONE_FORMAT_RULES}
```

---

## 📋 Form Validation Templates

### Location Entry Form
```shortcode
{LOCATION_FORM}
form_fields:
  location_name:
    type: text
    required: true
    validation: "{{location_name_validation}}"
    placeholder: "Enter city or location name"
    help_text: "Official name of the city or location"
    
  coordinates:
    latitude:
      type: number
      required: true
      step: 0.000001
      min: -90
      max: 90
      validation: "{{latitude_validation}}"
      placeholder: "e.g., 40.7128"
      
    longitude:
      type: number
      required: true
      step: 0.000001
      min: -180
      max: 180
      validation: "{{longitude_validation}}"
      placeholder: "e.g., -74.0060"
      
  country:
    type: select
    required: true
    options: "{{country_options}}"
    searchable: true
    placeholder: "Select country"
    
  timezone:
    type: select
    required: true
    options: "{{timezone_options}}"
    dependent_on: country
    searchable: true
    placeholder: "Select timezone"
    
  population:
    type: number
    required: false
    min: 0
    max: 50000000
    placeholder: "e.g., 8336817"
    help_text: "Current population estimate"

validation_messages:
  location_name_required: "Location name is required"
  location_name_min_length: "Location name must be at least 2 characters"
  coordinates_required: "Coordinates are required"
  latitude_range: "Latitude must be between -90 and 90 degrees"
  longitude_range: "Longitude must be between -180 and 180 degrees"
  timezone_required: "Timezone selection is required"
  timezone_invalid: "Please select a valid IANA timezone"
{/LOCATION_FORM}
```

### Batch Location Import
```shortcode
{BATCH_LOCATION_IMPORT}
import_format: csv
required_columns: [name, latitude, longitude, country_code, timezone]
optional_columns: [state_province, population, elevation, founded_year]

csv_template:
  headers: "name,latitude,longitude,country_code,timezone,state_province,population"
  sample_row: "New York City,40.7128,-74.0060,US,America/New_York,New York,8336817"

validation_rules:
  max_rows: 1000
  encoding: utf-8
  delimiter: comma
  quote_char: double_quote
  
error_handling:
  skip_invalid_rows: true
  generate_error_report: true
  max_errors: 100
  
batch_validation:
  duplicate_detection: true
  coordinate_validation: strict
  timezone_verification: true
  country_code_validation: true
{/BATCH_LOCATION_IMPORT}
```

---

*This comprehensive validation system ensures accurate and consistent location and timezone data capture across all uDOS mapping applications.*
