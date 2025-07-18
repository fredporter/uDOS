# 🧪 jq - JSON Processor for uDOS

**jq** is a lightweight and flexible command-line JSON processor. Essential for uDOS data processing, API responses, and configuration management.

## 🚀 Installation

### Manual Installation
```bash
./uCode/packages/install-jq.sh
```

## 🎯 Usage

### Basic JSON Processing
```bash
# Pretty print JSON
echo '{"name":"uDOS","version":"1.0"}' | jq .

# Extract specific field
echo '{"name":"uDOS","version":"1.0"}' | jq .name

# Extract multiple fields
echo '{"name":"uDOS","version":"1.0","status":"active"}' | jq '{name, version}'

# Array processing
echo '[{"id":1,"name":"mission1"},{"id":2,"name":"mission2"}]' | jq '.[].name'
```

## 🧠 uDOS Integration Workflows

### Mission Data Processing
```bash
# Process mission manifest
cat ./uMemory/missions/manifest.json | jq '.missions[] | select(.status == "active")'

# Extract mission IDs
cat ./uMemory/missions/manifest.json | jq '.missions[].id'

# Format mission data for dashboard
cat ./uMemory/missions/manifest.json | jq '{
  total: (.missions | length),
  active: [.missions[] | select(.status == "active")] | length,
  completed: [.missions[] | select(.status == "completed")] | length
}'
```

### Package Management
```bash
# Parse package manifest
cat ./package/manifest.json | jq '.packages.utils | keys'

# Check package installation status
cat ./package/manifest.json | jq '.packages.utils.ripgrep'

# List auto-install packages
cat ./package/manifest.json | jq '.packages | to_entries[] | select(.value | has("auto_install") and .auto_install == true) | .key'
```

### Configuration Processing
```bash
# Extract VS Code settings
cat .vscode/settings.json | jq '.["uDOS.userRole"]'

# Process task definitions
cat .vscode/tasks.json | jq '.tasks[] | select(.group == "build") | .label'

# Format configuration for display
cat .vscode/launch.json | jq '.configurations[] | {name, type, program}'
```

### API Response Processing
```bash
# Process GitHub API responses (for Chester AI integration)
curl -s "https://api.github.com/repos/user/repo/releases/latest" | jq '.tag_name'

# Extract download URLs
curl -s "https://api.github.com/repos/user/repo/releases/latest" | jq '.assets[] | {name: .name, url: .browser_download_url}'

# Process Gemini API responses
echo '{"response":"Hello","status":"success"}' | jq '.response'
```

## 🔧 Advanced Features

### Data Transformation
```bash
# Transform array to object
echo '[{"id":1,"name":"test"}]' | jq 'map({(.name): .id}) | add'

# Group by field
echo '[{"type":"util","name":"rg"},{"type":"util","name":"fd"}]' | jq 'group_by(.type)'

# Calculate statistics
echo '[1,2,3,4,5]' | jq 'add / length'
```

### Conditional Processing
```bash
# Conditional selection
cat data.json | jq 'if .status == "active" then .name else empty end'

# Multiple conditions
cat data.json | jq 'select(.status == "active" and .priority > 1)'

# Default values
cat data.json | jq '.description // "No description available"'
```

### Output Formatting
```bash
# Raw output (no quotes)
echo '{"message":"Hello World"}' | jq -r .message

# Compact output
echo '{"a": 1, "b": 2}' | jq -c .

# Tab-separated values
echo '[{"name":"A","value":1},{"name":"B","value":2}]' | jq -r '.[] | [.name, .value] | @tsv'
```

## 📊 uDOS Dashboard Integration

### Statistics Generation
```bash
# Mission statistics for dashboard
./uCode/json-processor.sh missions stats | jq '{
  missions: .total,
  active: .active_count,
  completion_rate: (.completed_count / .total * 100 | floor)
}'

# Package installation status
./uCode/json-processor.sh packages status | jq 'map(select(.installed)) | length'
```

### Report Generation
```bash
# Generate installation report
cat ./package/manifest.json | jq '{
  total_packages: [.packages | to_entries[]] | length,
  auto_install: [.packages | to_entries[] | select(.value.auto_install == true)] | length,
  categories: [.packages | keys] | unique
}'
```

## ⚙️ Configuration

Create `~/.jq` for custom functions:
```jq
# Custom function for uDOS mission processing
def mission_summary: {
  id: .id,
  name: .name,
  status: .status,
  progress: (.completed_steps / .total_steps * 100 | floor)
};

# Function for package status
def package_status: {
  name: .name,
  installed: (.install_status // false),
  required: (.auto_install // false)
};
```

## 🔧 uDOS Integration Features

- **Mission Management**: Process mission data and statistics
- **Package Processing**: Handle package manifests and status
- **Configuration Management**: Parse and transform config files
- **API Integration**: Process external API responses
- **Dashboard Data**: Generate formatted data for dashboards
- **uScript Support**: Available in automation workflows

---

*Powerful JSON processing for uDOS data workflows.*
