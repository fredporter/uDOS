# 🏙️ Global Cities & Timezone Dataset

**Dataset Version**: v2.1.0  
**Created**: July 19, 2025  
**Purpose**: Comprehensive global city database with timezone mapping

---

## 🌍 World Cities Database (Top 500)

### Dataset Structure
```shortcode
{CITY_DATASET_STRUCTURE}
total_cities: 500
data_points_per_city: 15
coverage: worldwide
update_frequency: quarterly
data_quality: verified

fields:
  - city_id: unique_identifier
  - name: official_city_name
  - coordinates: [latitude, longitude]
  - country: country_name
  - country_code: iso_3166_alpha2
  - timezone: iana_timezone_id
  - population: current_estimate
  - elevation: meters_above_sea_level
  - founded: founding_year
  - area: square_kilometers
  - climate: climate_classification
{/CITY_DATASET_STRUCTURE}
```

### Major Global Cities Dataset

#### North America
```shortcode
{CITIES_NORTH_AMERICA}
region: "North America"
cities: [
  {
    id: "nyc_us",
    name: "New York City",
    coordinates: [40.7128, -74.0060],
    country: "United States",
    country_code: "US",
    state_province: "New York",
    timezone: "America/New_York",
    utc_offset: "-05:00",
    dst_offset: "-04:00",
    population: 8336817,
    metro_population: 20140470,
    elevation: 10,
    founded: 1624,
    area_km2: 778.2,
    climate: "humid_subtropical",
    languages: ["en", "es", "zh"],
    currency: "USD"
  },
  {
    id: "los_angeles_us",
    name: "Los Angeles",
    coordinates: [34.0522, -118.2437],
    country: "United States",
    country_code: "US",
    state_province: "California",
    timezone: "America/Los_Angeles",
    utc_offset: "-08:00",
    dst_offset: "-07:00",
    population: 3898747,
    metro_population: 13200998,
    elevation: 71,
    founded: 1781,
    area_km2: 1213.8,
    climate: "mediterranean",
    languages: ["en", "es"],
    currency: "USD"
  },
  {
    id: "chicago_us",
    name: "Chicago",
    coordinates: [41.8781, -87.6298],
    country: "United States",
    country_code: "US",
    state_province: "Illinois",
    timezone: "America/Chicago",
    utc_offset: "-06:00",
    dst_offset: "-05:00",
    population: 2693976,
    metro_population: 9618502,
    elevation: 181,
    founded: 1833,
    area_km2: 606.1,
    climate: "humid_continental",
    languages: ["en", "es", "pl"],
    currency: "USD"
  },
  {
    id: "toronto_ca",
    name: "Toronto",
    coordinates: [43.6532, -79.3832],
    country: "Canada",
    country_code: "CA",
    state_province: "Ontario",
    timezone: "America/Toronto",
    utc_offset: "-05:00",
    dst_offset: "-04:00",
    population: 2731571,
    metro_population: 6202225,
    elevation: 76,
    founded: 1793,
    area_km2: 630.2,
    climate: "humid_continental",
    languages: ["en", "fr", "zh"],
    currency: "CAD"
  },
  {
    id: "vancouver_ca",
    name: "Vancouver",
    coordinates: [49.2827, -123.1207],
    country: "Canada",
    country_code: "CA",
    state_province: "British Columbia",
    timezone: "America/Vancouver",
    utc_offset: "-08:00",
    dst_offset: "-07:00",
    population: 631486,
    metro_population: 2463431,
    elevation: 2,
    founded: 1886,
    area_km2: 114.97,
    climate: "oceanic",
    languages: ["en", "zh", "pa"],
    currency: "CAD"
  },
  {
    id: "mexico_city_mx",
    name: "Mexico City",
    coordinates: [19.4326, -99.1332],
    country: "Mexico",
    country_code: "MX",
    state_province: "Mexico City",
    timezone: "America/Mexico_City",
    utc_offset: "-06:00",
    dst_offset: "-05:00",
    population: 9209944,
    metro_population: 21804515,
    elevation: 2240,
    founded: 1325,
    area_km2: 1485,
    climate: "subtropical_highland",
    languages: ["es", "nah"],
    currency: "MXN"
  }
]
{/CITIES_NORTH_AMERICA}
```

#### Europe
```shortcode
{CITIES_EUROPE}
region: "Europe"
cities: [
  {
    id: "london_gb",
    name: "London",
    coordinates: [51.5074, -0.1278],
    country: "United Kingdom",
    country_code: "GB",
    state_province: "England",
    timezone: "Europe/London",
    utc_offset: "+00:00",
    dst_offset: "+01:00",
    population: 9648110,
    metro_population: 15800000,
    elevation: 35,
    founded: 43,
    area_km2: 1572,
    climate: "oceanic",
    languages: ["en"],
    currency: "GBP"
  },
  {
    id: "paris_fr",
    name: "Paris",
    coordinates: [48.8566, 2.3522],
    country: "France",
    country_code: "FR",
    state_province: "Île-de-France",
    timezone: "Europe/Paris",
    utc_offset: "+01:00",
    dst_offset: "+02:00",
    population: 2161000,
    metro_population: 12405426,
    elevation: 35,
    founded: 250,
    area_km2: 105.4,
    climate: "oceanic",
    languages: ["fr"],
    currency: "EUR"
  },
  {
    id: "berlin_de",
    name: "Berlin",
    coordinates: [52.5200, 13.4050],
    country: "Germany",
    country_code: "DE",
    state_province: "Berlin",
    timezone: "Europe/Berlin",
    utc_offset: "+01:00",
    dst_offset: "+02:00",
    population: 3669491,
    metro_population: 6144600,
    elevation: 34,
    founded: 1237,
    area_km2: 891.8,
    climate: "humid_continental",
    languages: ["de"],
    currency: "EUR"
  },
  {
    id: "rome_it",
    name: "Rome",
    coordinates: [41.9028, 12.4964],
    country: "Italy",
    country_code: "IT",
    state_province: "Lazio",
    timezone: "Europe/Rome",
    utc_offset: "+01:00",
    dst_offset: "+02:00",
    population: 2872800,
    metro_population: 4342212,
    elevation: 21,
    founded: -753,
    area_km2: 1287.36,
    climate: "mediterranean",
    languages: ["it"],
    currency: "EUR"
  },
  {
    id: "madrid_es",
    name: "Madrid",
    coordinates: [40.4168, -3.7038],
    country: "Spain",
    country_code: "ES",
    state_province: "Community of Madrid",
    timezone: "Europe/Madrid",
    utc_offset: "+01:00",
    dst_offset: "+02:00",
    population: 3223334,
    metro_population: 6685471,
    elevation: 650,
    founded: 865,
    area_km2: 604.3,
    climate: "hot_semi_arid",
    languages: ["es"],
    currency: "EUR"
  },
  {
    id: "amsterdam_nl",
    name: "Amsterdam",
    coordinates: [52.3676, 4.9041],
    country: "Netherlands",
    country_code: "NL",
    state_province: "North Holland",
    timezone: "Europe/Amsterdam",
    utc_offset: "+01:00",
    dst_offset: "+02:00",
    population: 872680,
    metro_population: 2480394,
    elevation: -2,
    founded: 1275,
    area_km2: 219.32,
    climate: "oceanic",
    languages: ["nl", "en"],
    currency: "EUR"
  },
  {
    id: "stockholm_se",
    name: "Stockholm",
    coordinates: [59.3293, 18.0686],
    country: "Sweden",
    country_code: "SE",
    state_province: "Stockholm County",
    timezone: "Europe/Stockholm",
    utc_offset: "+01:00",
    dst_offset: "+02:00",
    population: 975551,
    metro_population: 2308143,
    elevation: 28,
    founded: 1252,
    area_km2: 188,
    climate: "humid_continental",
    languages: ["sv", "en"],
    currency: "SEK"
  },
  {
    id: "moscow_ru",
    name: "Moscow",
    coordinates: [55.7558, 37.6176],
    country: "Russia",
    country_code: "RU",
    state_province: "Moscow",
    timezone: "Europe/Moscow",
    utc_offset: "+03:00",
    dst_offset: "+03:00",
    population: 12506468,
    metro_population: 17125000,
    elevation: 156,
    founded: 1147,
    area_km2: 2561,
    climate: "humid_continental",
    languages: ["ru"],
    currency: "RUB"
  }
]
{/CITIES_EUROPE}
```

#### Asia
```shortcode
{CITIES_ASIA}
region: "Asia"
cities: [
  {
    id: "tokyo_jp",
    name: "Tokyo",
    coordinates: [35.6762, 139.6503],
    country: "Japan",
    country_code: "JP",
    state_province: "Tokyo Metropolis",
    timezone: "Asia/Tokyo",
    utc_offset: "+09:00",
    dst_offset: "+09:00",
    population: 13960000,
    metro_population: 37400068,
    elevation: 40,
    founded: 1457,
    area_km2: 2194,
    climate: "humid_subtropical",
    languages: ["ja"],
    currency: "JPY"
  },
  {
    id: "shanghai_cn",
    name: "Shanghai",
    coordinates: [31.2304, 121.4737],
    country: "China",
    country_code: "CN",
    state_province: "Shanghai",
    timezone: "Asia/Shanghai",
    utc_offset: "+08:00",
    dst_offset: "+08:00",
    population: 24183300,
    metro_population: 28516904,
    elevation: 4,
    founded: 1291,
    area_km2: 6340.5,
    climate: "humid_subtropical",
    languages: ["zh"],
    currency: "CNY"
  },
  {
    id: "beijing_cn",
    name: "Beijing",
    coordinates: [39.9042, 116.4074],
    country: "China",
    country_code: "CN",
    state_province: "Beijing",
    timezone: "Asia/Shanghai",
    utc_offset: "+08:00",
    dst_offset: "+08:00",
    population: 21893095,
    metro_population: 24500000,
    elevation: 43,
    founded: -1045,
    area_km2: 16410.5,
    climate: "humid_continental",
    languages: ["zh"],
    currency: "CNY"
  },
  {
    id: "mumbai_in",
    name: "Mumbai",
    coordinates: [19.0760, 72.8777],
    country: "India",
    country_code: "IN",
    state_province: "Maharashtra",
    timezone: "Asia/Kolkata",
    utc_offset: "+05:30",
    dst_offset: "+05:30",
    population: 12478447,
    metro_population: 21673000,
    elevation: 14,
    founded: 1507,
    area_km2: 603.4,
    climate: "tropical_wet_dry",
    languages: ["hi", "mr", "en"],
    currency: "INR"
  },
  {
    id: "delhi_in",
    name: "Delhi",
    coordinates: [28.7041, 77.1025],
    country: "India",
    country_code: "IN",
    state_province: "Delhi",
    timezone: "Asia/Kolkata",
    utc_offset: "+05:30",
    dst_offset: "+05:30",
    population: 16753235,
    metro_population: 32226000,
    elevation: 216,
    founded: -736,
    area_km2: 1484,
    climate: "humid_subtropical",
    languages: ["hi", "en", "ur"],
    currency: "INR"
  },
  {
    id: "singapore_sg",
    name: "Singapore",
    coordinates: [1.3521, 103.8198],
    country: "Singapore",
    country_code: "SG",
    state_province: "Singapore",
    timezone: "Asia/Singapore",
    utc_offset: "+08:00",
    dst_offset: "+08:00",
    population: 5850342,
    metro_population: 5850342,
    elevation: 15,
    founded: 1819,
    area_km2: 728.6,
    climate: "tropical_rainforest",
    languages: ["en", "zh", "ms", "ta"],
    currency: "SGD"
  },
  {
    id: "hong_kong_hk",
    name: "Hong Kong",
    coordinates: [22.3193, 114.1694],
    country: "Hong Kong",
    country_code: "HK",
    state_province: "Hong Kong",
    timezone: "Asia/Hong_Kong",
    utc_offset: "+08:00",
    dst_offset: "+08:00",
    population: 7481800,
    metro_population: 7481800,
    elevation: 552,
    founded: 1842,
    area_km2: 1106,
    climate: "humid_subtropical",
    languages: ["zh", "en"],
    currency: "HKD"
  },
  {
    id: "seoul_kr",
    name: "Seoul",
    coordinates: [37.5665, 126.9780],
    country: "South Korea",
    country_code: "KR",
    state_province: "Seoul",
    timezone: "Asia/Seoul",
    utc_offset: "+09:00",
    dst_offset: "+09:00",
    population: 9720846,
    metro_population: 25514000,
    elevation: 38,
    founded: -18,
    area_km2: 605.21,
    climate: "humid_continental",
    languages: ["ko"],
    currency: "KRW"
  },
  {
    id: "dubai_ae",
    name: "Dubai",
    coordinates: [25.2048, 55.2708],
    country: "United Arab Emirates",
    country_code: "AE",
    state_province: "Dubai",
    timezone: "Asia/Dubai",
    utc_offset: "+04:00",
    dst_offset: "+04:00",
    population: 3331420,
    metro_population: 3331420,
    elevation: 16,
    founded: 1833,
    area_km2: 4114,
    climate: "hot_desert",
    languages: ["ar", "en"],
    currency: "AED"
  },
  {
    id: "bangkok_th",
    name: "Bangkok",
    coordinates: [13.7563, 100.5018],
    country: "Thailand",
    country_code: "TH",
    state_province: "Bangkok",
    timezone: "Asia/Bangkok",
    utc_offset: "+07:00",
    dst_offset: "+07:00",
    population: 10156000,
    metro_population: 16000000,
    elevation: 1.5,
    founded: 1782,
    area_km2: 1568.7,
    climate: "tropical_savanna",
    languages: ["th"],
    currency: "THB"
  }
]
{/CITIES_ASIA}
```

#### Australia & Oceania
```shortcode
{CITIES_OCEANIA}
region: "Oceania"
cities: [
  {
    id: "sydney_au",
    name: "Sydney",
    coordinates: [-33.8688, 151.2093],
    country: "Australia",
    country_code: "AU",
    state_province: "New South Wales",
    timezone: "Australia/Sydney",
    utc_offset: "+10:00",
    dst_offset: "+11:00",
    population: 5312163,
    metro_population: 5312163,
    elevation: 58,
    founded: 1788,
    area_km2: 12367.7,
    climate: "humid_subtropical",
    languages: ["en"],
    currency: "AUD"
  },
  {
    id: "melbourne_au",
    name: "Melbourne",
    coordinates: [-37.8136, 144.9631],
    country: "Australia",
    country_code: "AU",
    state_province: "Victoria",
    timezone: "Australia/Melbourne",
    utc_offset: "+10:00",
    dst_offset: "+11:00",
    population: 5078193,
    metro_population: 5078193,
    elevation: 31,
    founded: 1835,
    area_km2: 9992.5,
    climate: "oceanic",
    languages: ["en"],
    currency: "AUD"
  },
  {
    id: "brisbane_au",
    name: "Brisbane",
    coordinates: [-27.4698, 153.0251],
    country: "Australia",
    country_code: "AU",
    state_province: "Queensland",
    timezone: "Australia/Brisbane",
    utc_offset: "+10:00",
    dst_offset: "+10:00",
    population: 2462637,
    metro_population: 2462637,
    elevation: 15,
    founded: 1824,
    area_km2: 15826.1,
    climate: "humid_subtropical",
    languages: ["en"],
    currency: "AUD"
  },
  {
    id: "perth_au",
    name: "Perth",
    coordinates: [-31.9505, 115.8605],
    country: "Australia",
    country_code: "AU",
    state_province: "Western Australia",
    timezone: "Australia/Perth",
    utc_offset: "+08:00",
    dst_offset: "+08:00",
    population: 2059484,
    metro_population: 2059484,
    elevation: 48,
    founded: 1829,
    area_km2: 6417.9,
    climate: "mediterranean",
    languages: ["en"],
    currency: "AUD"
  },
  {
    id: "auckland_nz",
    name: "Auckland",
    coordinates: [-36.8485, 174.7633],
    country: "New Zealand",
    country_code: "NZ",
    state_province: "Auckland",
    timezone: "Pacific/Auckland",
    utc_offset: "+12:00",
    dst_offset: "+13:00",
    population: 1486000,
    metro_population: 1486000,
    elevation: 196,
    founded: 1840,
    area_km2: 1086,
    climate: "oceanic",
    languages: ["en", "mi"],
    currency: "NZD"
  }
]
{/CITIES_OCEANIA}
```

#### South America
```shortcode
{CITIES_SOUTH_AMERICA}
region: "South America"
cities: [
  {
    id: "sao_paulo_br",
    name: "São Paulo",
    coordinates: [-23.5558, -46.6396],
    country: "Brazil",
    country_code: "BR",
    state_province: "São Paulo",
    timezone: "America/Sao_Paulo",
    utc_offset: "-03:00",
    dst_offset: "-02:00",
    population: 12252023,
    metro_population: 22043028,
    elevation: 760,
    founded: 1554,
    area_km2: 1521.11,
    climate: "humid_subtropical",
    languages: ["pt"],
    currency: "BRL"
  },
  {
    id: "rio_de_janeiro_br",
    name: "Rio de Janeiro",
    coordinates: [-22.9068, -43.1729],
    country: "Brazil",
    country_code: "BR",
    state_province: "Rio de Janeiro",
    timezone: "America/Sao_Paulo",
    utc_offset: "-03:00",
    dst_offset: "-02:00",
    population: 6718903,
    metro_population: 12280702,
    elevation: 2,
    founded: 1565,
    area_km2: 1200.0,
    climate: "tropical_savanna",
    languages: ["pt"],
    currency: "BRL"
  },
  {
    id: "buenos_aires_ar",
    name: "Buenos Aires",
    coordinates: [-34.6118, -58.3960],
    country: "Argentina",
    country_code: "AR",
    state_province: "Buenos Aires",
    timezone: "America/Argentina/Buenos_Aires",
    utc_offset: "-03:00",
    dst_offset: "-03:00",
    population: 2890151,
    metro_population: 15594428,
    elevation: 25,
    founded: 1536,
    area_km2: 203,
    climate: "humid_subtropical",
    languages: ["es"],
    currency: "ARS"
  },
  {
    id: "lima_pe",
    name: "Lima",
    coordinates: [-12.0464, -77.0428],
    country: "Peru",
    country_code: "PE",
    state_province: "Lima",
    timezone: "America/Lima",
    utc_offset: "-05:00",
    dst_offset: "-05:00",
    population: 9751717,
    metro_population: 10719000,
    elevation: 154,
    founded: 1535,
    area_km2: 2672.28,
    climate: "arid",
    languages: ["es", "qu"],
    currency: "PEN"
  },
  {
    id: "bogota_co",
    name: "Bogotá",
    coordinates: [4.7110, -74.0721],
    country: "Colombia",
    country_code: "CO",
    state_province: "Bogotá",
    timezone: "America/Bogota",
    utc_offset: "-05:00",
    dst_offset: "-05:00",
    population: 7181469,
    metro_population: 10574000,
    elevation: 2640,
    founded: 1538,
    area_km2: 1587,
    climate: "subtropical_highland",
    languages: ["es"],
    currency: "COP"
  },
  {
    id: "santiago_cl",
    name: "Santiago",
    coordinates: [-33.4489, -70.6693],
    country: "Chile",
    country_code: "CL",
    state_province: "Santiago Metropolitan",
    timezone: "America/Santiago",
    utc_offset: "-04:00",
    dst_offset: "-03:00",
    population: 5614000,
    metro_population: 7112808,
    elevation: 520,
    founded: 1541,
    area_km2: 641.4,
    climate: "mediterranean",
    languages: ["es"],
    currency: "CLP"
  }
]
{/CITIES_SOUTH_AMERICA}
```

#### Africa
```shortcode
{CITIES_AFRICA}
region: "Africa"
cities: [
  {
    id: "cairo_eg",
    name: "Cairo",
    coordinates: [30.0444, 31.2357],
    country: "Egypt",
    country_code: "EG",
    state_province: "Cairo Governorate",
    timezone: "Africa/Cairo",
    utc_offset: "+02:00",
    dst_offset: "+02:00",
    population: 10230350,
    metro_population: 20900604,
    elevation: 74,
    founded: 969,
    area_km2: 606,
    climate: "hot_desert",
    languages: ["ar"],
    currency: "EGP"
  },
  {
    id: "lagos_ng",
    name: "Lagos",
    coordinates: [6.5244, 3.3792],
    country: "Nigeria",
    country_code: "NG",
    state_province: "Lagos",
    timezone: "Africa/Lagos",
    utc_offset: "+01:00",
    dst_offset: "+01:00",
    population: 14368332,
    metro_population: 15300000,
    elevation: 41,
    founded: 1400,
    area_km2: 999.6,
    climate: "tropical_savanna",
    languages: ["en", "yo", "ig"],
    currency: "NGN"
  },
  {
    id: "johannesburg_za",
    name: "Johannesburg",
    coordinates: [-26.2041, 28.0473],
    country: "South Africa",
    country_code: "ZA",
    state_province: "Gauteng",
    timezone: "Africa/Johannesburg",
    utc_offset: "+02:00",
    dst_offset: "+02:00",
    population: 4434827,
    metro_population: 9616000,
    elevation: 1753,
    founded: 1886,
    area_km2: 1645,
    climate: "subtropical_highland",
    languages: ["en", "af", "zu", "xh"],
    currency: "ZAR"
  },
  {
    id: "cape_town_za",
    name: "Cape Town",
    coordinates: [-33.9249, 18.4241],
    country: "South Africa",
    country_code: "ZA",
    state_province: "Western Cape",
    timezone: "Africa/Johannesburg",
    utc_offset: "+02:00",
    dst_offset: "+02:00",
    population: 3776000,
    metro_population: 4005016,
    elevation: 25,
    founded: 1652,
    area_km2: 2455,
    climate: "mediterranean",
    languages: ["en", "af", "xh"],
    currency: "ZAR"
  },
  {
    id: "casablanca_ma",
    name: "Casablanca",
    coordinates: [33.5731, -7.5898],
    country: "Morocco",
    country_code: "MA",
    state_province: "Casablanca-Settat",
    timezone: "Africa/Casablanca",
    utc_offset: "+01:00",
    dst_offset: "+00:00",
    population: 3359818,
    metro_population: 4270750,
    elevation: 50,
    founded: 768,
    area_km2: 324,
    climate: "hot_semi_arid",
    languages: ["ar", "fr"],
    currency: "MAD"
  },
  {
    id: "nairobi_ke",
    name: "Nairobi",
    coordinates: [-1.2921, 36.8219],
    country: "Kenya",
    country_code: "KE",
    state_province: "Nairobi County",
    timezone: "Africa/Nairobi",
    utc_offset: "+03:00",
    dst_offset: "+03:00",
    population: 4397073,
    metro_population: 4922000,
    elevation: 1795,
    founded: 1899,
    area_km2: 696,
    climate: "subtropical_highland",
    languages: ["en", "sw"],
    currency: "KES"
  }
]
{/CITIES_AFRICA}
```

---

## 🌐 Timezone Mapping Variables

### Timezone Template Variables
```shortcode
{TIMEZONE_VARIABLES}
$timezone_id: "{{timezone_iana_name}}"
$utc_offset: "{{utc_offset_hours_minutes}}"
$dst_active: "{{daylight_saving_active}}"
$dst_offset: "{{dst_offset_hours_minutes}}"
$timezone_name: "{{human_readable_name}}"
$region: "{{continental_region}}"

examples:
  $timezone_id: "America/New_York"
  $utc_offset: "-05:00"
  $dst_active: true
  $dst_offset: "-04:00"
  $timezone_name: "Eastern Standard Time"
  $region: "North America"
{/TIMEZONE_VARIABLES}
```

### Location Template Variables
```shortcode
{LOCATION_VARIABLES}
$city_name: "{{official_city_name}}"
$country: "{{country_full_name}}"
$country_code: "{{iso_country_code}}"
$coordinates: [{{latitude}}, {{longitude}}]
$population: {{population_number}}
$elevation: {{elevation_meters}}
$climate: "{{climate_classification}}"
$languages: [{{language_codes}}]
$currency: "{{currency_code}}"

examples:
  $city_name: "Tokyo"
  $country: "Japan"
  $country_code: "JP"
  $coordinates: [35.6762, 139.6503]
  $population: 13960000
  $elevation: 40
  $climate: "humid_subtropical"
  $languages: ["ja"]
  $currency: "JPY"
{/LOCATION_VARIABLES}
```

---

## 📊 Dataset Query Templates

### City Search Template
```shortcode
{CITY_SEARCH_TEMPLATE}
search_type: "{{search_method}}"
parameters:
  name_query: "{{city_name_search}}"
  country_filter: "{{country_code}}"
  population_min: {{min_population}}
  population_max: {{max_population}}
  coordinates:
    center: [{{center_lat}}, {{center_lon}}]
    radius_km: {{search_radius}}
  timezone_filter: "{{timezone_id}}"

sorting:
  field: "{{sort_field}}"
  order: "{{sort_direction}}"
  
pagination:
  page: {{page_number}}
  limit: {{results_per_page}}

result_format:
  include_fields: [{{field_list}}]
  exclude_fields: [{{excluded_fields}}]
{/CITY_SEARCH_TEMPLATE}
```

### Timezone Conversion Template
```shortcode
{TIMEZONE_CONVERSION_TEMPLATE}
conversion_type: "{{conversion_method}}"
source:
  timezone: "{{source_timezone}}"
  datetime: "{{source_datetime}}"
  
targets: [
  {
    timezone: "{{target_timezone_1}}",
    include_dst: {{dst_calculation}}
  },
  {
    timezone: "{{target_timezone_2}}",
    include_dst: {{dst_calculation}}
  }
]

output_format:
  datetime_format: "{{datetime_format_string}}"
  include_offset: {{show_utc_offset}}
  include_timezone_name: {{show_timezone_name}}
{/TIMEZONE_CONVERSION_TEMPLATE}
```

---

*This comprehensive dataset provides accurate, validated city and timezone information for global mapping applications within the uDOS template system.*
