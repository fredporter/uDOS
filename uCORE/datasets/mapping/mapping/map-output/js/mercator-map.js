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
