# 🧾 uDOS Setup Prompts - Dataset Integrated

## 👤 Username  
DATA: username  
ASK: Enter your preferred username  
DEFAULT: agentdigital  
TYPE: freetext  
DATASET: none

---

## 🔒 Password  
DATA: password  
ASK: Enter a password (optional)  
DEFAULT: none  
TYPE: password  
DATASET: none

---

## 📍 Location  
DATA: location  
ASK: Enter your location code or city name  
DEFAULT: London  
TYPE: location_lookup  
DATASET: locationMap
SAMPLE: London, New York, Tokyo, Sydney, Paris

---

## 🕒 Timezone  
DATA: timezone  
ASK: Enter your timezone  
DEFAULT: UTC  
TYPE: timezone_lookup  
DATASET: timezoneMap
SAMPLE: UTC, EST, PST, JST, AEST

---

## ⏱️ UTC Offset  
DATA: utc_offset  
ASK: (auto-detect from timezone)  
DEFAULT: +00:00  
TYPE: auto_generate  
DATASET: timezoneMap

---

## 🌍 Country
DATA: country
ASK: (auto-detect from location)
DEFAULT: Unknown
TYPE: auto_generate
DATASET: countryMap

---

## 🗣️ Language
DATA: language
ASK: Preferred language code
DEFAULT: EN
TYPE: language_lookup
DATASET: languageMap
SAMPLE: EN, ES, FR, DE, JA

---

## 💰 Currency
DATA: currency
ASK: (auto-detect from country)
DEFAULT: USD
TYPE: auto_generate
DATASET: currencyMap

---

*Template Version: 1.1.0 - Dataset Integrated*
*Compatible with: uDOS v1.7.1 Template System*  