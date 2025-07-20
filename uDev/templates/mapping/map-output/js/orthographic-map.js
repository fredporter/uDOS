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
