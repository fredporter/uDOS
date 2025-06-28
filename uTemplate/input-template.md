# 🧩 uDOS Input Field Template

Use this format to define user prompts in Markdown. These fields will be rendered dynamically in CLI during onboarding or config steps.

---

## 🏷️ <Display Label>  
DATA: <data_key>  
ASK: <Question to display in CLI>  
DEFAULT: <default_value>  
TYPE: <freetext | password | choice | date | number>  
OPTIONS: [option1, option2, ...]  # only for TYPE: choice  
REQUIRED: <true | false>          # optional — assumed true if not present  
HELP: <Additional context or tips shown on hover or on request>  # optional  

---

### 📌 Example:

```md
## 👤 Username  
DATA: username  
ASK: Enter your preferred username  
DEFAULT: agentdigital  
TYPE: freetext  

## 🎨 Theme  
DATA: theme  
ASK: Choose your interface theme  
DEFAULT: ascii  
TYPE: choice  
OPTIONS: [ascii, dark, light]  
```
