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
