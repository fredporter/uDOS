# GitHub Diagram Formats - Examples

This directory contains example GeoJSON maps and ASCII STL 3D models for survival scenarios.

## GeoJSON Examples

### survival_area_map.geojson
Complete survival area map with:
- **Camp Alpha** - Main shelter location (point)
- **Freshwater Spring** - Water source (point)
- **Trail to Water** - Path from camp to water (line)
- **Foraging Zone** - Food gathering area (polygon)

**Use in guides:**
```markdown
# Navigation: Finding Water

```geojson
{
  "type": "FeatureCollection",
  "features": [...]
}
```
```

## ASCII STL Examples

### shelter/a_frame.stl
A-frame shelter design:
- 3m length × 4m width × 2m height
- 45-degree roof pitch
- Basic triangular structure

### tools/hand_axe.stl
Stone hand axe model:
- Teardrop shape
- 2.5 units long
- 1.5 units wide at head

**Use in guides:**
```markdown
# Shelter: A-Frame Construction

```stl
solid a_frame_shelter
  facet normal 0.0 0.707 0.707
    ...
  endfacet
endsolid a_frame_shelter
```
```

## Creating New Examples

### GeoJSON Maps
```bash
GEODIAGRAM GEO CREATE point        # Single location
GEODIAGRAM GEO CREATE line         # Path/route
GEODIAGRAM GEO CREATE polygon      # Area/zone
GEODIAGRAM GEO CREATE multi        # Multiple features
```

### ASCII STL Models
```bash
GEODIAGRAM STL CREATE shelter      # A-frame structure
GEODIAGRAM STL CREATE tool         # Hand axe
GEODIAGRAM STL CREATE trap         # Deadfall trap
GEODIAGRAM STL CREATE cube         # Test cube
```

## Integration with Knowledge Guides

Examples can be embedded directly in markdown guides:

**Water Guide with Map:**
```markdown
# Water Sources Map

```geojson
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "properties": {"name": "Spring"},
    "geometry": {"type": "Point", "coordinates": [-122.42, 37.77]}
  }]
}
```
```

**Shelter Guide with 3D Model:**
```markdown
# A-Frame Shelter Design

```stl
solid a_frame
  facet normal 0 0.707 0.707
    outer loop
      vertex 0 0 0
      vertex 3 2 0
      vertex 0 0 4
    endloop
  endfacet
endsolid
```
```

## Viewing Options

### GeoJSON
- **GitHub**: Automatic map rendering
- **geojson.io**: Online editor/viewer
- **QGIS**: Desktop GIS software
- **Leaflet.js**: Web mapping library

### ASCII STL
- **GitHub**: Automatic 3D rendering
- **ViewSTL.com**: Online viewer
- **Blender**: 3D modeling software
- **MeshLab**: Mesh processing tool

## File Locations

```
extensions/play/data/
├── examples/
│   └── survival_area_map.geojson
└── models/
    ├── shelter/
    │   ├── a_frame.stl
    │   ├── lean_to.stl
    │   └── debris_hut.stl
    └── tools/
        ├── hand_axe.stl
        ├── bow_drill.stl
        └── fish_spear.stl
```

## Next Steps

1. Create more survival-specific examples
2. Add real-world coordinate data
3. Test GitHub rendering
4. Document in knowledge guides
5. Add to GUIDE system templates

Version: 1.1.15
Last updated: December 2, 2025
