#!/bin/bash
# Mission Mapping Integration for uDOS v1.1.0
# Visualizes missions and milestones on the Advanced Mapping System

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
UTEMPLATE="${UHOME}/uTemplate"
MAPPING_DIR="${UTEMPLATE}/mapping"

# Generate GeoJSON data for missions
generate_mission_geojson() {
    local geojson_file="${MAPPING_DIR}/mission-locations.geojson"
    
    echo "🗺️  Generating mission GeoJSON data..."
    
    # Start GeoJSON structure
    cat > "$geojson_file" << 'EOF'
{
  "type": "FeatureCollection",
  "features": [
EOF

    local first_feature=true
    
    # Process each mission
    if [[ -d "${UMEM}/missions" ]]; then
        for mission_file in "${UMEM}/missions"/*.md; do
            if [[ -f "$mission_file" ]]; then
                # Extract mission data
                local mission_id=$(basename "$mission_file" .md)
                local mission_name=$(grep "^# 🎯 Mission:" "$mission_file" | sed 's/^# 🎯 Mission: //' | tr -d '\n\r')
                local created_date=$(grep "**Created**:" "$mission_file" | sed 's/.*Created\*\*: //' | awk '{print $1}')
                local status=$(grep "**Status**:" "$mission_file" | sed 's/.*Status\*\*: //' | tr -d '\n\r')
                
                # Extract location coordinates
                local location_line=$(grep "**Location**:" "$mission_file" | head -1)
                local lat lon
                if [[ -n "$location_line" ]]; then
                    lat=$(echo "$location_line" | sed 's/.*\[\([^,]*\),.*/\1/' | tr -d '[]')
                    lon=$(echo "$location_line" | sed 's/.*,\s*\([^\]]*\).*/\1/' | tr -d '[]')
                else
                    # Default location if none specified
                    lat="0"
                    lon="0"
                fi
                
                # Skip if coordinates are invalid
                if [[ "$lat" == "0" && "$lon" == "0" ]]; then
                    continue
                fi
                
                # Count milestones for this mission
                local milestone_count=0
                if [[ -d "${UMEM}/milestones" ]]; then
                    milestone_count=$(find "${UMEM}/milestones" -name "${mission_id}-*.md" -type f | wc -l | tr -d ' ')
                fi
                
                # Add comma if not first feature
                if [[ "$first_feature" != true ]]; then
                    echo "," >> "$geojson_file"
                fi
                first_feature=false
                
                # Add mission feature to GeoJSON
                cat >> "$geojson_file" << EOF
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [$lon, $lat]
      },
      "properties": {
        "mission_id": "$mission_id",
        "name": "$mission_name",
        "status": "$status",
        "created": "$created_date",
        "milestone_count": $milestone_count,
        "icon": "mission",
        "color": "#4CAF50",
        "description": "uDOS Mission: $mission_name\\nStatus: $status\\nMilestones: $milestone_count"
      }
    }
EOF
            fi
        done
    fi
    
    # Close GeoJSON structure
    echo "" >> "$geojson_file"
    echo "  ]" >> "$geojson_file"
    echo "}" >> "$geojson_file"
    
    echo "✅ Mission GeoJSON generated: $geojson_file"
}

# Create enhanced mapping demo with mission integration
create_mission_mapping_demo() {
    local demo_file="${MAPPING_DIR}/mission-mapping-demo.html"
    
    echo "🗺️  Creating mission mapping demo..."
    
    cat > "$demo_file" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>uDOS Mission Mapping System</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/topojson@3"></script>
    <style>
        body {
            background: #0a0a0f;
            color: #00ff7f;
            font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
            margin: 0;
            padding: 20px;
            overflow-x: auto;
        }
        
        .header {
            text-align: center;
            padding: 20px;
            border: 2px solid #00ff7f;
            border-radius: 10px;
            margin-bottom: 20px;
            background: rgba(0, 255, 127, 0.05);
        }
        
        .mapping-container {
            display: flex;
            gap: 20px;
        }
        
        .map-area {
            flex: 2;
            border: 2px solid #00ff7f;
            border-radius: 10px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.5);
        }
        
        .control-panel {
            flex: 1;
            border: 2px solid #00ff7f;
            border-radius: 10px;
            padding: 20px;
            background: rgba(0, 255, 127, 0.05);
            max-height: 500px;
            overflow-y: auto;
        }
        
        .mission-marker {
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .mission-marker:hover {
            stroke-width: 3px;
            r: 8;
        }
        
        .mission-info {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff7f;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
        }
        
        .status-active { fill: #4CAF50; }
        .status-completed { fill: #2196F3; }
        .status-planned { fill: #FFC107; }
        
        button {
            background: #00ff7f;
            color: #0a0a0f;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
            font-family: inherit;
            font-size: 12px;
        }
        
        button:hover {
            background: #00cc66;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🗺️ uDOS Mission Mapping System v1.1.0</h1>
        <p>Visualizing missions and milestones across the virtual world</p>
    </div>
    
    <div class="mapping-container">
        <div class="map-area">
            <svg id="mission-map" width="800" height="500"></svg>
        </div>
        
        <div class="control-panel">
            <h3>🎯 Mission Control</h3>
            <div id="mission-list">
                Loading mission data...
            </div>
            
            <h3>🗺️ Map Controls</h3>
            <button onclick="zoomToFit()">📍 Zoom to Missions</button>
            <button onclick="toggleProjection()">🌍 Toggle Projection</button>
            <button onclick="refreshMissions()">🔄 Refresh Data</button>
            
            <h3>📊 Statistics</h3>
            <div id="mission-stats">
                <div>Total Missions: <span id="total-missions">0</span></div>
                <div>Active Missions: <span id="active-missions">0</span></div>
                <div>Milestones: <span id="total-milestones">0</span></div>
            </div>
        </div>
    </div>

    <script>
        // Map setup
        const svg = d3.select("#mission-map");
        const width = 800;
        const height = 500;
        
        let currentProjection = "mercator";
        let projections = {
            mercator: d3.geoMercator(),
            orthographic: d3.geoOrthographic(),
            equalEarth: d3.geoEqualEarth(),
            naturalEarth: d3.geoNaturalEarth1()
        };
        
        let projection = projections[currentProjection]
            .scale(130)
            .translate([width / 2, height / 2]);
            
        let path = d3.geoPath().projection(projection);
        let zoom = d3.zoom().scaleExtent([1, 8]).on("zoom", zoomed);
        
        svg.call(zoom);
        
        let mapGroup = svg.append("g");
        let missionData = null;
        
        // Load world map and missions
        Promise.all([
            d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json"),
            loadMissionData()
        ]).then(function([world, missions]) {
            // Draw world map
            mapGroup.append("g")
                .selectAll("path")
                .data(topojson.feature(world, world.objects.countries).features)
                .enter().append("path")
                .attr("d", path)
                .attr("fill", "#1e1e2e")
                .attr("stroke", "#00ff7f")
                .attr("stroke-width", 0.5);
            
            // Draw missions
            drawMissions(missions);
            updateMissionList(missions);
            updateStatistics(missions);
        });
        
        function loadMissionData() {
            // In a real implementation, this would load from the GeoJSON file
            // For demo, we'll use the current mission data
            return Promise.resolve({
                type: "FeatureCollection",
                features: [
                    {
                        type: "Feature",
                        geometry: {
                            type: "Point",
                            coordinates: [-73.9712, 40.7831]
                        },
                        properties: {
                            mission_id: "complete-udos-v1-1-0-development",
                            name: "Complete uDOS v1.1.0 Development",
                            status: "🚀 Active",
                            milestone_count: 3,
                            description: "Finalize all core systems"
                        }
                    }
                ]
            });
        }
        
        function drawMissions(missions) {
            missionData = missions;
            
            mapGroup.selectAll(".mission-marker").remove();
            
            mapGroup.selectAll(".mission-marker")
                .data(missions.features)
                .enter().append("circle")
                .attr("class", "mission-marker")
                .attr("cx", d => projection(d.geometry.coordinates)[0])
                .attr("cy", d => projection(d.geometry.coordinates)[1])
                .attr("r", 6)
                .attr("fill", "#4CAF50")
                .attr("stroke", "#00ff7f")
                .attr("stroke-width", 2)
                .on("click", function(event, d) {
                    showMissionInfo(d);
                })
                .append("title")
                .text(d => d.properties.description);
        }
        
        function showMissionInfo(mission) {
            alert(`Mission: ${mission.properties.name}\nStatus: ${mission.properties.status}\nMilestones: ${mission.properties.milestone_count}`);
        }
        
        function updateMissionList(missions) {
            const listContainer = d3.select("#mission-list");
            listContainer.html("");
            
            missions.features.forEach(mission => {
                const missionDiv = listContainer.append("div")
                    .attr("class", "mission-info");
                
                missionDiv.append("div")
                    .style("font-weight", "bold")
                    .text(mission.properties.name);
                    
                missionDiv.append("div")
                    .text(`Status: ${mission.properties.status}`);
                    
                missionDiv.append("div")
                    .text(`Milestones: ${mission.properties.milestone_count}`);
                    
                missionDiv.append("button")
                    .text("📍 Locate")
                    .on("click", () => {
                        const coords = projection(mission.geometry.coordinates);
                        svg.transition().duration(1000)
                            .call(zoom.transform, d3.zoomIdentity
                                .translate(width/2, height/2)
                                .scale(3)
                                .translate(-coords[0], -coords[1]));
                    });
            });
        }
        
        function updateStatistics(missions) {
            const totalMissions = missions.features.length;
            const activeMissions = missions.features.filter(m => 
                m.properties.status.includes("Active")).length;
            const totalMilestones = missions.features.reduce((sum, m) => 
                sum + (m.properties.milestone_count || 0), 0);
            
            d3.select("#total-missions").text(totalMissions);
            d3.select("#active-missions").text(activeMissions);
            d3.select("#total-milestones").text(totalMilestones);
        }
        
        function zoomed(event) {
            const {transform} = event;
            mapGroup.attr("transform", transform);
        }
        
        function zoomToFit() {
            svg.transition().duration(1000)
                .call(zoom.transform, d3.zoomIdentity);
        }
        
        function toggleProjection() {
            const projectionNames = Object.keys(projections);
            const currentIndex = projectionNames.indexOf(currentProjection);
            currentProjection = projectionNames[(currentIndex + 1) % projectionNames.length];
            
            projection = projections[currentProjection]
                .scale(130)
                .translate([width / 2, height / 2]);
            path = d3.geoPath().projection(projection);
            
            // Redraw map
            mapGroup.selectAll("path")
                .transition().duration(1000)
                .attr("d", path);
                
            // Redraw missions
            if (missionData) {
                drawMissions(missionData);
            }
        }
        
        function refreshMissions() {
            loadMissionData().then(missions => {
                drawMissions(missions);
                updateMissionList(missions);
                updateStatistics(missions);
            });
        }
    </script>
</body>
</html>
EOF
    
    echo "✅ Mission mapping demo created: $demo_file"
}

# Main execution
case "${1:-all}" in
    "geojson")
        generate_mission_geojson
        ;;
    "demo")
        create_mission_mapping_demo
        ;;
    "all"|"generate")
        generate_mission_geojson
        create_mission_mapping_demo
        echo "🗺️  Mission mapping integration complete!"
        echo "    📍 GeoJSON: ${MAPPING_DIR}/mission-locations.geojson"
        echo "    🗺️  Demo: ${MAPPING_DIR}/mission-mapping-demo.html"
        ;;
    *)
        echo "Usage: $0 [geojson|demo|all]"
        echo "  geojson - Generate mission location GeoJSON"
        echo "  demo    - Create interactive mapping demo"
        echo "  all     - Generate both GeoJSON and demo"
        ;;
esac
