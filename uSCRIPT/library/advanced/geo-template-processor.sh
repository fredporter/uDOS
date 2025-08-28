#!/bin/bash
# uDOS Map Shortcode Processor
# Processes mapping shortcodes and generates interactive visualizations

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR"
OUTPUT_DIR="./map-output"
ASSETS_DIR="./map-assets"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}🗺️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              🗺️ uDOS Map Shortcode Processor                   ║"
    echo "║              Advanced Geospatial Template Engine               ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Create directory structure
setup_directories() {
    mkdir -p "$OUTPUT_DIR"/{html,js,css,data,layers}
    mkdir -p "$ASSETS_DIR"/{datasets,projections,styles,icons}
    
    log_info "Directory structure created"
}

# Extract shortcodes from markdown files
extract_shortcodes() {
    local input_file="$1"
    local output_file="$2"
    
    log_info "Extracting shortcodes from: $input_file"
    
    # Extract all shortcodes and their content
    grep -n "^{[A-Z_]*}" "$input_file" > "$output_file.index" 2>/dev/null || true
    
    # Process each shortcode type
    process_map_shortcodes "$input_file" "$output_file"
    process_layer_shortcodes "$input_file" "$output_file"
    process_dataset_shortcodes "$input_file" "$output_file"
    process_timeline_shortcodes "$input_file" "$output_file"
}

# Process map projection shortcodes
process_map_shortcodes() {
    local input_file="$1"
    local output_base="$2"
    
    # Extract MAP_MERCATOR shortcodes
    sed -n '/^{MAP_MERCATOR}/,/^{\/MAP_MERCATOR}/p' "$input_file" | while IFS= read -r line; do
        if [[ $line =~ ^{MAP_MERCATOR} ]]; then
            log_info "Processing Mercator projection..."
            generate_mercator_map "$output_base"
        fi
    done
    
    # Extract MAP_ROBINSON shortcodes
    sed -n '/^{MAP_ROBINSON}/,/^{\/MAP_ROBINSON}/p' "$input_file" | while IFS= read -r line; do
        if [[ $line =~ ^{MAP_ROBINSON} ]]; then
            log_info "Processing Robinson projection..."
            generate_robinson_map "$output_base"
        fi
    done
    
    # Extract MAP_ORTHOGRAPHIC shortcodes
    sed -n '/^{MAP_ORTHOGRAPHIC}/,/^{\/MAP_ORTHOGRAPHIC}/p' "$input_file" | while IFS= read -r line; do
        if [[ $line =~ ^{MAP_ORTHOGRAPHIC} ]]; then
            log_info "Processing Orthographic projection..."
            generate_orthographic_map "$output_base"
        fi
    done
}

# Process layer shortcodes
process_layer_shortcodes() {
    local input_file="$1"
    local output_base="$2"
    
    # Process all layer types
    local layer_types=("ATMOSPHERE" "AVIATION" "CLOUDS" "SURFACE" "SUBSURFACE" "GEOLOGICAL" "CORE")
    
    for layer_type in "${layer_types[@]}"; do
        sed -n "/^{LAYER_$layer_type}/,/^{\/LAYER_$layer_type}/p" "$input_file" | while IFS= read -r line; do
            if [[ $line =~ ^{LAYER_$layer_type} ]]; then
                log_info "Processing $layer_type layer..."
                generate_layer_definition "$layer_type" "$output_base"
            fi
        done
    done
}

# Process dataset shortcodes
process_dataset_shortcodes() {
    local input_file="$1"
    local output_base="$2"
    
    # Extract dataset registry
    sed -n '/^{DATASET_REGISTRY}/,/^{\/DATASET_REGISTRY}/p' "$input_file" > "$output_base.datasets.tmp"
    
    if [ -s "$output_base.datasets.tmp" ]; then
        log_info "Processing dataset registry..."
        generate_dataset_config "$output_base"
    fi
    
    # Process visualization shortcodes
    local viz_types=("CHOROPLETH" "POINTS" "FLOW" "HEATMAP")
    
    for viz_type in "${viz_types[@]}"; do
        sed -n "/^{VIZ_$viz_type}/,/^{\/VIZ_$viz_type}/p" "$input_file" | while IFS= read -r line; do
            if [[ $line =~ ^{VIZ_$viz_type} ]]; then
                log_info "Processing $viz_type visualization..."
                generate_visualization_config "$viz_type" "$output_base"
            fi
        done
    done
}

# Process timeline shortcodes
process_timeline_shortcodes() {
    local input_file="$1"
    local output_base="$2"
    
    local timeline_types=("HISTORICAL" "REALTIME" "PROJECTION")
    
    for timeline_type in "${timeline_types[@]}"; do
        sed -n "/^{TIMELINE_$timeline_type}/,/^{\/TIMELINE_$timeline_type}/p" "$input_file" | while IFS= read -r line; do
            if [[ $line =~ ^{TIMELINE_$timeline_type} ]]; then
                log_info "Processing $timeline_type timeline..."
                generate_timeline_config "$timeline_type" "$output_base"
            fi
        done
    done
}

# Generate Mercator projection map
generate_mercator_map() {
    local output_base="$1"
    
    cat > "$OUTPUT_DIR/js/mercator-map.js" << 'EOF'
// Mercator Projection Map Generator
class MercatorMap {
    constructor(config) {
        this.config = config;
        this.projection = d3.geoMercator()
            .center([config.center_lon || 0, config.center_lat || 0])
            .scale(config.zoom_level || 150)
            .translate([config.width/2, config.height/2]);
    }
    
    render(container) {
        const svg = d3.select(container)
            .append('svg')
            .attr('width', this.config.width)
            .attr('height', this.config.height);
            
        const path = d3.geoPath()
            .projection(this.projection);
            
        // Load and render world data
        d3.json('data/world-110m.json').then(world => {
            svg.append('g')
                .selectAll('path')
                .data(topojson.feature(world, world.objects.countries).features)
                .enter().append('path')
                .attr('d', path)
                .attr('class', 'country')
                .style('fill', '#ccc')
                .style('stroke', '#fff');
        });
    }
}
EOF
    
    log_success "Mercator map generator created"
}

# Generate Robinson projection map
generate_robinson_map() {
    local output_base="$1"
    
    cat > "$OUTPUT_DIR/js/robinson-map.js" << 'EOF'
// Robinson Projection Map Generator
class RobinsonMap {
    constructor(config) {
        this.config = config;
        this.projection = d3.geoRobinson()
            .scale(config.scale || 160)
            .translate([config.width/2, config.height/2]);
    }
    
    render(container) {
        const svg = d3.select(container)
            .append('svg')
            .attr('width', this.config.width)
            .attr('height', this.config.height);
            
        const path = d3.geoPath()
            .projection(this.projection);
            
        // Graticule
        const graticule = d3.geoGraticule();
        
        svg.append('path')
            .datum(graticule)
            .attr('class', 'graticule')
            .attr('d', path)
            .style('fill', 'none')
            .style('stroke', '#ddd');
            
        // World outline
        svg.append('path')
            .datum({type: "Sphere"})
            .attr('class', 'sphere')
            .attr('d', path)
            .style('fill', 'none')
            .style('stroke', '#000');
    }
}
EOF
    
    log_success "Robinson map generator created"
}

# Generate Orthographic projection map
generate_orthographic_map() {
    local output_base="$1"
    
    cat > "$OUTPUT_DIR/js/orthographic-map.js" << 'EOF'
// Orthographic Projection Map Generator (3D Globe)
class OrthographicMap {
    constructor(config) {
        this.config = config;
        this.projection = d3.geoOrthographic()
            .scale(config.scale || 250)
            .translate([config.width/2, config.height/2])
            .clipAngle(90);
    }
    
    render(container) {
        const svg = d3.select(container)
            .append('svg')
            .attr('width', this.config.width)
            .attr('height', this.config.height);
            
        const path = d3.geoPath()
            .projection(this.projection);
            
        // Enable rotation
        const drag = d3.drag()
            .on('drag', (event) => {
                const rotate = this.projection.rotate();
                const k = 75 / this.projection.scale();
                this.projection.rotate([
                    rotate[0] + event.dx * k,
                    rotate[1] - event.dy * k
                ]);
                svg.selectAll('path').attr('d', path);
            });
            
        svg.call(drag);
        
        // Globe sphere
        svg.append('path')
            .datum({type: "Sphere"})
            .attr('class', 'sphere')
            .attr('d', path)
            .style('fill', '#1f77b4')
            .style('stroke', '#000');
    }
}
EOF
    
    log_success "Orthographic map generator created"
}

# Generate layer definition
generate_layer_definition() {
    local layer_type="$1"
    local output_base="$2"
    
    cat > "$OUTPUT_DIR/layers/$(echo ${layer_type} | tr '[:upper:]' '[:lower:]')-layer.json" << EOF
{
    "name": "${layer_type} Layer",
    "type": "${layer_type,,}",
    "altitude": $(get_layer_altitude "$layer_type"),
    "opacity": 0.7,
    "visible": true,
    "data_sources": [],
    "visualization": {
        "type": "$(get_visualization_type "$layer_type")",
        "animation": true,
        "color_scheme": "$(get_color_scheme "$layer_type")"
    },
    "update_interval": "$(get_update_interval "$layer_type")",
    "metadata": {
        "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
        "version": "1.0.0"
    }
}
EOF
    
    log_success "Layer definition created: ${layer_type,,}"
}

# Generate dataset configuration
generate_dataset_config() {
    local output_base="$1"
    
    cat > "$OUTPUT_DIR/data/dataset-config.json" << 'EOF'
{
    "datasets": [
        {
            "name": "World Bank Development Indicators",
            "id": "wb_wdi",
            "type": "socioeconomic",
            "coverage": "global",
            "update_frequency": "annual",
            "api_endpoint": "https://api.worldbank.org/v2/",
            "layers": ["country_data", "economic_indicators"],
            "format": "json"
        },
        {
            "name": "NASA Earth Observation",
            "id": "nasa_eo",
            "type": "environmental",
            "coverage": "global",
            "update_frequency": "daily",
            "api_endpoint": "https://earthdata.nasa.gov/",
            "layers": ["satellite_imagery", "climate_data"],
            "format": "netcdf"
        },
        {
            "name": "OpenStreetMap",
            "id": "osm",
            "type": "geographic",
            "coverage": "global",
            "update_frequency": "realtime",
            "api_endpoint": "https://api.openstreetmap.org/",
            "layers": ["roads", "buildings", "points_of_interest"],
            "format": "geojson"
        }
    ]
}
EOF
    
    log_success "Dataset configuration created"
}

# Generate visualization configuration
generate_visualization_config() {
    local viz_type="$1"
    local output_base="$2"
    
    cat > "$OUTPUT_DIR/js/viz-${viz_type,,}.js" << EOF
// ${viz_type} Visualization Generator
class ${viz_type}Visualization {
    constructor(config) {
        this.config = config;
        this.setupVisualization();
    }
    
    setupVisualization() {
        switch(this.config.type) {
            case 'choropleth':
                this.setupChoropleth();
                break;
            case 'points':
                this.setupPointMap();
                break;
            case 'flow':
                this.setupFlowMap();
                break;
            case 'heatmap':
                this.setupHeatmap();
                break;
        }
    }
    
    render(container, data) {
        // Implementation specific to ${viz_type}
        console.log('Rendering ${viz_type} visualization');
    }
    
    update(newData) {
        // Update visualization with new data
        console.log('Updating ${viz_type} with new data');
    }
}
EOF
    
    log_success "Visualization config created: ${viz_type,,}"
}

# Generate timeline configuration
generate_timeline_config() {
    local timeline_type="$1"
    local output_base="$2"
    
    cat > "$OUTPUT_DIR/js/timeline-${timeline_type,,}.js" << EOF
// ${timeline_type} Timeline Generator
class ${timeline_type}Timeline {
    constructor(config) {
        this.config = config;
        this.currentTime = new Date();
        this.setupTimeline();
    }
    
    setupTimeline() {
        this.timeScale = d3.scaleTime()
            .domain([
                new Date(this.config.start_date || '1900-01-01'),
                new Date(this.config.end_date || '2100-12-31')
            ])
            .range([0, this.config.width || 800]);
    }
    
    render(container) {
        const svg = d3.select(container)
            .append('svg')
            .attr('width', this.config.width || 800)
            .attr('height', this.config.height || 100);
            
        // Add timeline axis
        const axis = d3.axisBottom(this.timeScale)
            .tickFormat(d3.timeFormat('%Y'));
            
        svg.append('g')
            .attr('class', 'timeline-axis')
            .attr('transform', 'translate(0, 50)')
            .call(axis);
    }
    
    animate() {
        // Timeline animation logic
        console.log('Animating ${timeline_type} timeline');
    }
}
EOF
    
    log_success "Timeline config created: ${timeline_type,,}"
}

# Generate main HTML interface
generate_html_interface() {
    cat > "$OUTPUT_DIR/html/map-interface.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>uDOS Interactive Map System</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/topojson@3"></script>
    <link rel="stylesheet" href="../css/map-styles.css">
</head>
<body>
    <div id="map-container">
        <div id="map-controls">
            <div class="control-panel">
                <h3>Layers</h3>
                <div id="layer-controls"></div>
            </div>
            <div class="control-panel">
                <h3>Time</h3>
                <div id="time-controls"></div>
            </div>
            <div class="control-panel">
                <h3>Data</h3>
                <div id="data-controls"></div>
            </div>
        </div>
        <div id="map-viewport">
            <div id="main-map"></div>
            <div id="timeline"></div>
        </div>
    </div>
    
    <script src="../js/map-core.js"></script>
    <script src="../js/mercator-map.js"></script>
    <script src="../js/robinson-map.js"></script>
    <script src="../js/orthographic-map.js"></script>
    <script>
        // Initialize map system
        const mapSystem = new uDOSMapSystem({
            container: '#main-map',
            width: 800,
            height: 600,
            defaultProjection: 'robinson'
        });
        
        mapSystem.initialize();
    </script>
</body>
</html>
EOF
    
    log_success "HTML interface generated"
}

# Generate CSS styles
generate_css_styles() {
    cat > "$OUTPUT_DIR/css/map-styles.css" << 'EOF'
/* uDOS Map System Styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #1a1a1a;
    color: #ffffff;
}

#map-container {
    display: flex;
    height: 100vh;
}

#map-controls {
    width: 300px;
    background-color: #2d2d2d;
    padding: 20px;
    overflow-y: auto;
}

.control-panel {
    margin-bottom: 20px;
    border: 1px solid #444;
    border-radius: 8px;
    padding: 15px;
}

.control-panel h3 {
    margin-top: 0;
    color: #4a9eff;
    border-bottom: 1px solid #444;
    padding-bottom: 10px;
}

#map-viewport {
    flex: 1;
    display: flex;
    flex-direction: column;
}

#main-map {
    flex: 1;
    background-color: #1a1a1a;
}

#timeline {
    height: 100px;
    background-color: #2d2d2d;
    border-top: 1px solid #444;
}

/* Map element styles */
.country {
    fill: #666;
    stroke: #fff;
    stroke-width: 0.5;
    cursor: pointer;
}

.country:hover {
    fill: #4a9eff;
}

.graticule {
    fill: none;
    stroke: #333;
    stroke-width: 0.5;
}

.sphere {
    fill: #1a1a1a;
    stroke: #4a9eff;
    stroke-width: 2;
}

/* Layer controls */
.layer-toggle {
    display: flex;
    align-items: center;
    margin: 10px 0;
}

.layer-toggle input[type="checkbox"] {
    margin-right: 10px;
}

.layer-toggle label {
    cursor: pointer;
    flex: 1;
}

/* Time controls */
.time-controls {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.time-slider {
    width: 100%;
}

.play-controls {
    display: flex;
    justify-content: center;
    gap: 10px;
}

.play-controls button {
    background-color: #4a9eff;
    border: none;
    border-radius: 4px;
    color: white;
    padding: 8px 12px;
    cursor: pointer;
}

.play-controls button:hover {
    background-color: #357abd;
}

/* Data visualization elements */
.choropleth {
    stroke: #fff;
    stroke-width: 0.5;
}

.flow-line {
    fill: none;
    stroke: #ff6b35;
    stroke-width: 2;
    opacity: 0.7;
}

.data-point {
    fill: #4a9eff;
    stroke: #fff;
    stroke-width: 1;
}

/* Animation classes */
.fade-in {
    animation: fadeIn 0.5s ease-in;
}

.fade-out {
    animation: fadeOut 0.5s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
}

/* Responsive design */
@media (max-width: 768px) {
    #map-container {
        flex-direction: column;
    }
    
    #map-controls {
        width: 100%;
        height: 200px;
    }
}
EOF
    
    log_success "CSS styles generated"
}

# Generate core JavaScript
generate_core_js() {
    cat > "$OUTPUT_DIR/js/map-core.js" << 'EOF'
// uDOS Map System Core
class uDOSMapSystem {
    constructor(config) {
        this.config = config;
        this.layers = new Map();
        this.datasets = new Map();
        this.timelines = new Map();
        this.currentProjection = config.defaultProjection || 'robinson';
        this.currentTime = new Date();
    }
    
    initialize() {
        this.setupContainer();
        this.loadLayers();
        this.loadDatasets();
        this.setupEventHandlers();
        this.render();
    }
    
    setupContainer() {
        this.container = d3.select(this.config.container);
        this.svg = this.container.append('svg')
            .attr('width', this.config.width)
            .attr('height', this.config.height);
    }
    
    loadLayers() {
        // Load layer definitions
        d3.json('layers/surface-layer.json').then(layer => {
            this.layers.set('surface', layer);
        });
        
        d3.json('layers/atmosphere-layer.json').then(layer => {
            this.layers.set('atmosphere', layer);
        });
    }
    
    loadDatasets() {
        // Load dataset configurations
        d3.json('data/dataset-config.json').then(config => {
            config.datasets.forEach(dataset => {
                this.datasets.set(dataset.id, dataset);
            });
        });
    }
    
    setupEventHandlers() {
        // Layer toggle handlers
        d3.selectAll('.layer-toggle input').on('change', (event) => {
            const layerId = event.target.dataset.layerId;
            this.toggleLayer(layerId, event.target.checked);
        });
        
        // Time control handlers
        d3.select('#play-button').on('click', () => {
            this.toggleTimeAnimation();
        });
    }
    
    render() {
        // Render active layers
        this.layers.forEach((layer, id) => {
            if (layer.visible) {
                this.renderLayer(id, layer);
            }
        });
    }
    
    renderLayer(id, layer) {
        // Layer-specific rendering logic
        switch(layer.type) {
            case 'surface':
                this.renderSurfaceLayer(layer);
                break;
            case 'atmosphere':
                this.renderAtmosphereLayer(layer);
                break;
            default:
                console.warn(`Unknown layer type: ${layer.type}`);
        }
    }
    
    renderSurfaceLayer(layer) {
        // Render geographic surface data
        d3.json('data/world-110m.json').then(world => {
            this.svg.selectAll('.country')
                .data(topojson.feature(world, world.objects.countries).features)
                .enter().append('path')
                .attr('class', 'country')
                .attr('d', this.getProjectionPath());
        });
    }
    
    renderAtmosphereLayer(layer) {
        // Render atmospheric data
        // Placeholder for atmospheric visualization
    }
    
    getProjectionPath() {
        let projection;
        
        switch(this.currentProjection) {
            case 'mercator':
                projection = d3.geoMercator();
                break;
            case 'robinson':
                projection = d3.geoRobinson();
                break;
            case 'orthographic':
                projection = d3.geoOrthographic();
                break;
            default:
                projection = d3.geoRobinson();
        }
        
        projection
            .scale(150)
            .translate([this.config.width/2, this.config.height/2]);
            
        return d3.geoPath().projection(projection);
    }
    
    toggleLayer(layerId, visible) {
        const layer = this.layers.get(layerId);
        if (layer) {
            layer.visible = visible;
            this.render();
        }
    }
    
    toggleTimeAnimation() {
        // Toggle time animation
        this.timeAnimationActive = !this.timeAnimationActive;
        
        if (this.timeAnimationActive) {
            this.startTimeAnimation();
        } else {
            this.stopTimeAnimation();
        }
    }
    
    startTimeAnimation() {
        // Start time-based animation
        this.timeInterval = setInterval(() => {
            this.updateTime();
        }, 1000);
    }
    
    stopTimeAnimation() {
        // Stop time-based animation
        if (this.timeInterval) {
            clearInterval(this.timeInterval);
        }
    }
    
    updateTime() {
        // Update current time and refresh time-dependent layers
        this.currentTime = new Date(this.currentTime.getTime() + 86400000); // Add 1 day
        this.render();
    }
}

// Utility functions
function formatTimestamp(date) {
    return date.toISOString().substr(0, 19) + 'Z';
}

function parseShortcode(content, shortcodeType) {
    const regex = new RegExp(`{${shortcodeType}}([\\s\\S]*?){\\/${shortcodeType}}`, 'g');
    const matches = [];
    let match;
    
    while ((match = regex.exec(content)) !== null) {
        matches.push(match[1].trim());
    }
    
    return matches;
}

function processShortcodeParameters(content) {
    const params = {};
    const lines = content.split('\n');
    
    lines.forEach(line => {
        const colonIndex = line.indexOf(':');
        if (colonIndex > 0) {
            const key = line.substring(0, colonIndex).trim();
            const value = line.substring(colonIndex + 1).trim();
            params[key] = value;
        }
    });
    
    return params;
}
EOF
    
    log_success "Core JavaScript generated"
}

# Helper functions
get_layer_altitude() {
    case "$1" in
        "ATMOSPHERE") echo "10000" ;;
        "AVIATION") echo "10000" ;;
        "CLOUDS") echo "2000" ;;
        "SURFACE") echo "0" ;;
        "SUBSURFACE") echo "-100" ;;
        "GEOLOGICAL") echo "-1000" ;;
        "CORE") echo "-6371000" ;;
        *) echo "0" ;;
    esac
}

get_visualization_type() {
    case "$1" in
        "ATMOSPHERE") echo "particle_system" ;;
        "AVIATION") echo "vector_paths" ;;
        "CLOUDS") echo "volumetric" ;;
        "SURFACE") echo "raster_vector_hybrid" ;;
        "SUBSURFACE") echo "cross_section" ;;
        "GEOLOGICAL") echo "stratigraphic" ;;
        "CORE") echo "scientific" ;;
        *) echo "standard" ;;
    esac
}

get_color_scheme() {
    case "$1" in
        "ATMOSPHERE") echo "plasma" ;;
        "AVIATION") echo "traffic" ;;
        "CLOUDS") echo "weather" ;;
        "SURFACE") echo "natural_earth" ;;
        "SUBSURFACE") echo "infrastructure" ;;
        "GEOLOGICAL") echo "geological" ;;
        "CORE") echo "scientific" ;;
        *) echo "default" ;;
    esac
}

get_update_interval() {
    case "$1" in
        "ATMOSPHERE") echo "1h" ;;
        "AVIATION") echo "30s" ;;
        "CLOUDS") echo "15min" ;;
        "SURFACE") echo "daily" ;;
        "SUBSURFACE") echo "monthly" ;;
        "GEOLOGICAL") echo "yearly" ;;
        "CORE") echo "static" ;;
        *) echo "daily" ;;
    esac
}

# Show usage
show_usage() {
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  process <file>     Process markdown file with map shortcodes"
    echo "  generate-all       Generate complete map system"
    echo "  serve              Start development server"
    echo "  help              Show this help"
    echo
    echo "Options:"
    echo "  --output <dir>     Output directory (default: ./map-output)"
    echo "  --assets <dir>     Assets directory (default: ./map-assets)"
    echo
    echo "Examples:"
    echo "  $0 process map-layers.md"
    echo "  $0 generate-all --output ./maps"
    echo "  $0 serve"
}

# Main command processor
main() {
    case "${1:-help}" in
        process)
            if [ $# -lt 2 ]; then
                log_error "Input file required"
                show_usage
                exit 1
            fi
            
            setup_directories
            extract_shortcodes "$2" "$OUTPUT_DIR/processed"
            generate_html_interface
            generate_css_styles
            generate_core_js
            log_success "Map processing complete! Output in: $OUTPUT_DIR"
            ;;
            
        generate-all)
            setup_directories
            generate_html_interface
            generate_css_styles
            generate_core_js
            
            # Generate sample configurations
            generate_layer_definition "SURFACE" "$OUTPUT_DIR/sample"
            generate_layer_definition "ATMOSPHERE" "$OUTPUT_DIR/sample"
            generate_dataset_config "$OUTPUT_DIR/sample"
            
            log_success "Complete map system generated! Output in: $OUTPUT_DIR"
            ;;
            
        serve)
            if command -v python3 &> /dev/null; then
                log_info "Starting development server at http://localhost:8000"
                cd "$OUTPUT_DIR" && python3 -m http.server 8000
            else
                log_error "Python3 required for development server"
                exit 1
            fi
            ;;
            
        help|--help|-h)
            show_usage
            ;;
            
        *)
            log_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
print_header
main "$@"
