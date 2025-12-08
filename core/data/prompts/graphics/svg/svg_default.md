---
id: svg_default
format: svg
version: 1.0.0
created: 2025-12-07T00:00:00
updated: 2025-12-07T00:00:00
author: uDOS Core Team
usage_count: 0
success_rate: 0.0
tags: [default, vector, diagram]
---

# Prompt: SVG Diagram Generation

## Purpose
Generate SVG vector graphics for technical diagrams, infographics, and illustrations.

## Input Variables
- {{input}}: Description of the graphic to create
- {{style}}: Visual style (technical/simple/detailed)
- {{complexity}}: Level of detail (simple/detailed/technical)

## System Prompt
You are an expert SVG diagram generator. Create a clean, well-structured SVG graphic based on:

Input: {{input}}
Style: {{style}}
Complexity: {{complexity}}

Requirements:
- Valid SVG XML syntax
- Proper viewBox and dimensions
- Clear visual hierarchy
- Appropriate use of shapes, paths, text
- Consistent styling
- Accessibility (titles, descriptions)
- Color scheme appropriate for {{style}}

Style Guidelines:
- technical: Blueprint style with grid, measurements, annotations (blues/grays)
- simple: Minimalist clean design with flat colors (pastels)
- detailed: Comprehensive with gradients, shadows, depth (full palette)

## Output Format
Complete SVG file starting with <?xml version="1.0"?>. Include proper namespace and viewBox.

## Examples
### Example 1: Water Filter System (Technical)
Input: "water filter system"
Style: "technical"
Output:
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">
  <title>Water Filter System</title>
  <desc>Technical diagram of a water filtration system</desc>
  
  <!-- Background grid -->
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e0e0e0" stroke-width="0.5"/>
    </pattern>
  </defs>
  <rect width="400" height="300" fill="url(#grid)"/>
  
  <!-- Input pipe -->
  <rect x="20" y="140" width="60" height="20" fill="#4a90e2" stroke="#2e5c8a" stroke-width="2"/>
  <text x="50" y="155" font-family="monospace" font-size="10" text-anchor="middle" fill="#fff">INPUT</text>
  
  <!-- Filter container -->
  <rect x="100" y="100" width="80" height="100" fill="#fff" stroke="#2e5c8a" stroke-width="2"/>
  <text x="140" y="90" font-family="monospace" font-size="12" text-anchor="middle" fill="#2e5c8a">FILTER</text>
  
  <!-- Filter layers -->
  <rect x="110" y="110" width="60" height="20" fill="#d4e6f1"/>
  <rect x="110" y="135" width="60" height="20" fill="#a9cce3"/>
  <rect x="110" y="160" width="60" height="20" fill="#7fb3d5"/>
  
  <!-- Output pipe -->
  <rect x="200" y="140" width="60" height="20" fill="#52c41a" stroke="#3a8f14" stroke-width="2"/>
  <text x="230" y="155" font-family="monospace" font-size="10" text-anchor="middle" fill="#fff">OUTPUT</text>
  
  <!-- Flow arrows -->
  <path d="M 80 150 L 95 150" stroke="#4a90e2" stroke-width="2" marker-end="url(#arrowblue)"/>
  <path d="M 185 150 L 195 150" stroke="#52c41a" stroke-width="2" marker-end="url(#arrowgreen)"/>
  
  <defs>
    <marker id="arrowblue" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto">
      <path d="M 0 0 L 5 3 L 0 6 Z" fill="#4a90e2"/>
    </marker>
    <marker id="arrowgreen" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto">
      <path d="M 0 0 L 5 3 L 0 6 Z" fill="#52c41a"/>
    </marker>
  </defs>
  
  <!-- Measurements -->
  <text x="140" y="220" font-family="monospace" font-size="10" text-anchor="middle" fill="#666">80mm × 100mm</text>
</svg>
```

### Example 2: Simple Flowchart
Input: "decision process"
Style: "simple"
Output:
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400">
  <title>Decision Process</title>
  
  <!-- Start -->
  <circle cx="150" cy="30" r="20" fill="#91d5ff" stroke="#1890ff" stroke-width="2"/>
  <text x="150" y="35" font-family="sans-serif" font-size="12" text-anchor="middle">Start</text>
  
  <!-- Process -->
  <rect x="100" y="80" width="100" height="40" rx="5" fill="#d3f261" stroke="#7cb305" stroke-width="2"/>
  <text x="150" y="105" font-family="sans-serif" font-size="12" text-anchor="middle">Process</text>
  
  <!-- Decision -->
  <path d="M 150 150 L 200 180 L 150 210 L 100 180 Z" fill="#ffd591" stroke="#fa8c16" stroke-width="2"/>
  <text x="150" y="185" font-family="sans-serif" font-size="12" text-anchor="middle">Valid?</text>
  
  <!-- Arrows -->
  <line x1="150" y1="50" x2="150" y2="80" stroke="#333" stroke-width="2"/>
  <line x1="150" y1="120" x2="150" y2="150" stroke="#333" stroke-width="2"/>
</svg>
```

## Notes
- Validate SVG syntax before output
- Use appropriate viewBox for content
- Include accessibility metadata (title, desc)
- Test rendering in browsers
- Keep file size reasonable (< 50KB)
- Use semantic grouping with <g> elements
