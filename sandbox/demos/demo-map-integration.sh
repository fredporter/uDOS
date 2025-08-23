#!/bin/bash
# uDOS Map System Integration Demo
# Demonstrates the complete mapping workflow

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="./mapping-demo"
MAP_LAYERS_FILE="$SCRIPT_DIR/map-layers.md"
PROCESSOR_SCRIPT="$SCRIPT_DIR/process-map-shortcodes.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}🗺️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_demo() { echo -e "${PURPLE}🎬 $1${NC}"; }

print_header() {
    echo -e "${BOLD}${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════════════╗"
    echo "║                🗺️ uDOS Map System Integration Demo                  ║"
    echo "║                Advanced Geospatial Visualization                     ║"
    echo "╚═══════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Demo functions
demo_shortcode_processing() {
    log_demo "DEMO 1: Processing Map Shortcodes"
    echo
    
    if [ ! -f "$MAP_LAYERS_FILE" ]; then
        log_error "Map layers file not found: $MAP_LAYERS_FILE"
        return 1
    fi
    
    log_info "Processing shortcodes from: $MAP_LAYERS_FILE"
    
    # Process the map shortcodes
    "$PROCESSOR_SCRIPT" process "$MAP_LAYERS_FILE" --output "$DEMO_DIR/output"
    
    echo
    log_info "Shortcode processing results:"
    echo "   • HTML Interface: $DEMO_DIR/output/html/map-interface.html"
    echo "   • JavaScript Core: $DEMO_DIR/output/js/map-core.js"
    echo "   • CSS Styles: $DEMO_DIR/output/css/map-styles.css"
    echo "   • Layer Configs: $DEMO_DIR/output/layers/"
    echo
}

demo_map_generation() {
    log_demo "DEMO 2: Complete Map System Generation"
    echo
    
    log_info "Generating complete interactive map system..."
    
    # Generate complete system
    "$PROCESSOR_SCRIPT" generate-all --output "$DEMO_DIR/complete"
    
    echo
    log_info "Generated map system components:"
    echo "   📊 Mercator Projection Maps"
    echo "   🌐 Robinson Projection Maps"
    echo "   🌍 3D Orthographic Globe"
    echo "   🌤️ Multi-layer Support (7+ layers)"
    echo "   📈 Timeline Integration"
    echo "   📊 Data Visualization"
    echo
}

demo_layer_visualization() {
    log_demo "DEMO 3: Virtual Layer Visualization"
    echo
    
    log_info "Creating ASCII visualization of layer stack..."
    
    cat << 'EOF'
    
    🌍 uDOS Virtual Layer Stack Visualization
    
    ┌─────────────────────────────────────────┐ +50,000m
    │           🛰️ SPACE LAYER               │
    │        Satellites & Orbital Data        │
    └─────────────────────────────────────────┘
    ┌─────────────────────────────────────────┐ +20,000m
    │        🌌 ATMOSPHERE LAYER             │
    │      Weather, Climate, Air Quality      │
    └─────────────────────────────────────────┘
    ┌─────────────────────────────────────────┐ +10,000m
    │         ✈️ AVIATION LAYER              │
    │       Flight Paths, Traffic Control     │
    └─────────────────────────────────────────┘
    ┌─────────────────────────────────────────┐ +2,000m
    │          ☁️ CLOUDS LAYER               │
    │       Precipitation, Storm Systems      │
    └─────────────────────────────────────────┘
    ┌─────────────────────────────────────────┐ 0m (Sea Level)
    │         🌍 SURFACE LAYER               │
    │    Geography, Cities, Infrastructure    │
    └─────────────────────────────────────────┘
    ┌─────────────────────────────────────────┐ -100m
    │       🚇 SUBSURFACE LAYER              │
    │     Tunnels, Utilities, Underground     │
    └─────────────────────────────────────────┘
    ┌─────────────────────────────────────────┐ -1,000m
    │       🪨 GEOLOGICAL LAYER              │
    │      Rock Formations, Mineral Data      │
    └─────────────────────────────────────────┘
    ┌─────────────────────────────────────────┐ -6,371km
    │         🌋 CORE LAYER                  │
    │       Earth's Core, Seismic Data        │
    └─────────────────────────────────────────┘
    
EOF

    echo
    log_info "Layer interaction capabilities:"
    echo "   • Real-time data updates"
    echo "   • Cross-layer analytics"
    echo "   • Temporal navigation"
    echo "   • Custom layer blending"
    echo
}

demo_temporal_navigation() {
    log_demo "DEMO 4: Temporal Navigation System"
    echo
    
    log_info "Demonstrating time-based navigation..."
    
    cat << 'EOF'
    
    ⏰ Temporal Coordinate System
    
    Past ←────────────────── Present ──────────────────→ Future
    
    📜 HISTORICAL LAYER     📊 REALTIME LAYER     🔮 PROJECTION LAYER
    ├─ 1900-2000           ├─ Live Data Feeds    ├─ Climate Models
    ├─ Census Data         ├─ Sensor Networks    ├─ Economic Forecasts
    ├─ War Records         ├─ Social Media       ├─ Population Growth
    └─ Climate History     └─ Market Data        └─ Technology Trends
    
    🎮 Time Controls:
    [◀◀] [◀] [⏸] [▶] [▶▶]  Speed: 1x  Mode: Historical
    
    📅 Current View: 2024-01-20 15:30:00 UTC
    
EOF

    echo
    log_info "Temporal features available:"
    echo "   • Historical data playback"
    echo "   • Real-time live updates"
    echo "   • Predictive modeling"
    echo "   • Custom time ranges"
    echo
}

demo_shortcode_examples() {
    log_demo "DEMO 5: Shortcode Template Examples"
    echo
    
    log_info "Sample shortcode usage patterns:"
    
    cat << 'EOF'
    
    💡 Basic Map Creation:
    {MAP_ROBINSON}
    center_lat: 40.7128
    center_lon: -74.0060
    zoom_level: 4
    width: 800
    height: 600
    {/MAP_ROBINSON}
    
    🌤️ Layer Configuration:
    {LAYER_ATMOSPHERE}
    data_source: nasa_weather
    update_interval: 1h
    visualization: particle_system
    opacity: 0.7
    {/LAYER_ATMOSPHERE}
    
    📊 Data Visualization:
    {VIZ_CHOROPLETH}
    dataset: world_bank_gdp
    color_scheme: blues
    data_field: gdp_per_capita
    projection: robinson
    {/VIZ_CHOROPLETH}
    
    ⏱️ Timeline Setup:
    {TIMELINE_HISTORICAL}
    start_date: 1950-01-01
    end_date: 2020-12-31
    animation_speed: 30fps
    markers: [1969-07-20, 1989-11-09, 2001-09-11]
    {/TIMELINE_HISTORICAL}
    
EOF

    echo
    log_info "Advanced shortcode features:"
    echo "   • Nested shortcode support"
    echo "   • Dynamic parameter injection"
    echo "   • Conditional rendering"
    echo "   • Cross-layer references"
    echo
}

demo_integration_workflow() {
    log_demo "DEMO 6: Complete Integration Workflow"
    echo
    
    log_info "End-to-end mapping workflow:"
    
    cat << 'EOF'
    
    📝 1. Create Map Template
       ├─ Define shortcodes in markdown
       ├─ Configure layers and data sources  
       ├─ Set up temporal parameters
       └─ Add visualization preferences
    
    🔄 2. Process with uDOS
       ├─ Extract shortcodes automatically
       ├─ Generate JavaScript components
       ├─ Create HTML interface
       └─ Compile CSS styles
    
    🌐 3. Deploy Interactive Map
       ├─ Serve via development server
       ├─ Integrate with uDOS dashboard
       ├─ Connect to live data feeds
       └─ Enable user interactions
    
    📊 4. Real-time Updates
       ├─ Automated data refresh
       ├─ Layer synchronization
       ├─ Performance monitoring
       └─ User analytics
    
EOF

    echo
    log_success "Integration workflow complete!"
    echo
}

demo_performance_features() {
    log_demo "DEMO 7: Performance & Optimization"
    echo
    
    log_info "Advanced performance features:"
    
    cat << 'EOF'
    
    ⚡ Performance Optimizations:
    
    🚀 Rendering Engine:
    ├─ WebGL acceleration for 3D layers
    ├─ Canvas 2D fallback for compatibility
    ├─ Tile-based loading for large datasets
    └─ Progressive enhancement
    
    💾 Data Management:
    ├─ Intelligent caching strategies
    ├─ Incremental data updates
    ├─ Compression algorithms
    └─ Background prefetching
    
    🎯 User Experience:
    ├─ Responsive design patterns
    ├─ Touch gesture support
    ├─ Keyboard navigation
    └─ Accessibility compliance
    
    📈 Monitoring:
    ├─ Real-time performance metrics
    ├─ Error tracking and reporting
    ├─ Usage analytics
    └─ Automated health checks
    
EOF

    echo
    log_info "Scalability features:"
    echo "   • Distributed data processing"
    echo "   • Edge computing integration"
    echo "   • Cloud storage backends"
    echo "   • Microservice architecture"
    echo
}

# Start development server
start_demo_server() {
    log_demo "STARTING: Interactive Demo Server"
    echo
    
    if [ -d "$DEMO_DIR/complete" ]; then
        log_info "Starting development server for interactive demo..."
        echo
        log_info "🌐 Server will be available at: http://localhost:8000"
        log_info "🗺️ Main interface: http://localhost:8000/html/map-interface.html"
        echo
        log_warning "Press Ctrl+C to stop the server"
        echo
        
        cd "$DEMO_DIR/complete" && python3 -m http.server 8000
    else
        log_error "Demo files not found. Run complete demo first."
        echo
        log_info "Try: $0 --complete"
    fi
}

# Show demo menu
show_menu() {
    echo -e "${BOLD}Demo Options:${NC}"
    echo "  1. Process Map Shortcodes"
    echo "  2. Generate Complete System"
    echo "  3. Layer Visualization"
    echo "  4. Temporal Navigation"
    echo "  5. Shortcode Examples"
    echo "  6. Integration Workflow"
    echo "  7. Performance Features"
    echo "  8. Run All Demos"
    echo "  9. Start Interactive Server"
    echo "  0. Exit"
    echo
}

# Run specific demo
run_demo() {
    case "$1" in
        1) demo_shortcode_processing ;;
        2) demo_map_generation ;;
        3) demo_layer_visualization ;;
        4) demo_temporal_navigation ;;
        5) demo_shortcode_examples ;;
        6) demo_integration_workflow ;;
        7) demo_performance_features ;;
        8) run_all_demos ;;
        9) start_demo_server ;;
        0) exit 0 ;;
        *) log_error "Invalid option: $1" ;;
    esac
}

# Run all demos
run_all_demos() {
    log_demo "Running Complete uDOS Map System Demo Suite"
    echo
    
    mkdir -p "$DEMO_DIR"
    
    demo_shortcode_processing
    demo_map_generation
    demo_layer_visualization
    demo_temporal_navigation
    demo_shortcode_examples
    demo_integration_workflow
    demo_performance_features
    
    echo
    log_success "🎉 Complete demo suite finished!"
    echo
    log_info "Next steps:"
    echo "   • Start interactive server: $0 --serve"
    echo "   • Explore generated files in: $DEMO_DIR/"
    echo "   • Integrate with your uDOS project"
    echo
}

# Show usage
show_usage() {
    echo "Usage: $0 [option]"
    echo
    echo "Options:"
    echo "  --complete       Run all demos"
    echo "  --serve          Start interactive demo server"
    echo "  --menu           Show interactive menu"
    echo "  --help           Show this help"
    echo
    echo "Interactive Mode:"
    echo "  $0 --menu"
    echo
    echo "Quick Start:"
    echo "  $0 --complete && $0 --serve"
}

# Main function
main() {
    case "${1:-menu}" in
        --complete)
            run_all_demos
            ;;
        --serve)
            start_demo_server
            ;;
        --menu)
            while true; do
                print_header
                show_menu
                read -p "Select demo (0-9): " choice
                echo
                run_demo "$choice"
                echo
                if [ "$choice" != "0" ]; then
                    read -p "Press Enter to continue..."
                fi
            done
            ;;
        --help|-h|help)
            show_usage
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
print_header
main "$@"
