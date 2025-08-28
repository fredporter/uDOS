/**
 * uDOS Map Generator v1.0.4.1
 * TypeScript-based world map generation using dataset integration
 * Enhanced with uDATA format support
 */

import * as fs from 'fs';
import * as path from 'path';
import { uDATAParser, uDATARecord } from './udataParser';

// Types for our datasets
interface LocationData {
  city_name: string;
  tile_reference: string;
  country: string;
  region: string;
  population_tier: string;
  location_type: string;
  latitude: number;
  longitude: number;
}

interface TerrainData {
  symbol: string;
  name: string;
  description: string;
  priority: number;
  usage_context: string;
}

interface TimezoneData {
  timezone_name: string;
  timezone_code: string;
  utc_offset: string;
  major_city: string;
  tile_reference: string;
  dst_observed: boolean;
  region: string;
}

interface MapTile {
  x: string;
  y: number;
  symbol: string;
  type: string;
  data?: any;
}

export class MapGenerator {
  private locationMap: LocationData[] = [];
  private terrainMap: TerrainData[] = [];
  private timezoneMap: TimezoneData[] = [];
  private mapGrid: MapTile[][] = [];

  // Map dimensions: 120 columns × 60 rows
  private readonly COLUMNS = 120;
  private readonly ROWS = 60;
  private readonly COLUMN_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

  constructor() {
    this.initializeGrid();
    this.loadDatasets();
  }

  /**
   * Initialize empty map grid with ocean tiles
   */
  private initializeGrid(): void {
    this.mapGrid = [];
    for (let row = 0; row < this.ROWS; row++) {
      const currentRow: MapTile[] = [];
      for (let col = 0; col < this.COLUMNS; col++) {
        const xCoord = this.numberToColumnId(col);
        currentRow.push({
          x: xCoord,
          y: row + 1,
          symbol: '🟦', // Ocean
          type: 'ocean'
        });
      }
      this.mapGrid.push(currentRow);
    }
  }

  /**
   * Convert column number to letter-based coordinate (A, B, ..., Z, AA, AB, ...)
   */
  private numberToColumnId(colNum: number): string {
    let result = '';
    let num = colNum;

    while (true) {
      result = this.COLUMN_LETTERS[num % 26] + result;
      num = Math.floor(num / 26);
      if (num === 0) break;
      num--;
    }

    return result;
  }

  /**
   * Convert tile reference (e.g., "AX14") to grid coordinates
   */
  private tileRefToCoords(tileRef: string): { col: number; row: number } | null {
    if (!tileRef || tileRef.length < 3) return null;

    const match = tileRef.match(/^([A-Z]+)(\d+)$/);
    if (!match) return null;

    const letters = match[1];
    const numbers = parseInt(match[2]);

    // Convert letters to column number
    let col = 0;
    for (let i = 0; i < letters.length; i++) {
      col = col * 26 + (letters.charCodeAt(i) - 65 + 1);
    }
    col--; // Convert to 0-based index

    const row = numbers - 1; // Convert to 0-based index

    if (col >= 0 && col < this.COLUMNS && row >= 0 && row < this.ROWS) {
      return { col, row };
    }

    return null;
  }

  /**
   * Load datasets from JSON files
   */
  private loadDatasets(): void {
    try {
      const uTemplateDir = path.resolve(__dirname, '../../');

      // Load location map
      const locationPath = path.join(uTemplateDir, 'datasets/locationMap.json');
      if (fs.existsSync(locationPath)) {
        this.locationMap = JSON.parse(fs.readFileSync(locationPath, 'utf8'));
      }

      // Load terrain map
      const terrainPath = path.join(uTemplateDir, 'datasets/mapTerrain.json');
      if (fs.existsSync(terrainPath)) {
        this.terrainMap = JSON.parse(fs.readFileSync(terrainPath, 'utf8'));
      }

      // Load timezone map
      const timezonePath = path.join(uTemplateDir, 'datasets/timezoneMap.json');
      if (fs.existsSync(timezonePath)) {
        this.timezoneMap = JSON.parse(fs.readFileSync(timezonePath, 'utf8'));
      }

      console.log(`✅ Loaded ${this.locationMap.length} locations, ${this.terrainMap.length} terrain types, ${this.timezoneMap.length} timezones`);
    } catch (error) {
      console.error('❌ Error loading datasets:', error);
    }
  }

  /**
   * Place cities on the map
   */
  private placeCities(): void {
    this.locationMap.forEach(location => {
      const coords = this.tileRefToCoords(location.tile_reference);
      if (coords) {
        const { col, row } = coords;
        let symbol = '🏙️'; // Default city

        // Use specific symbols based on location type
        switch (location.location_type) {
          case 'Airport': symbol = '✈️'; break;
          case 'World Wonder': symbol = '🗿'; break;
          case 'Island': symbol = '🏝️'; break;
          case 'Mountain': symbol = '⛰️'; break;
          default: symbol = '🏙️';
        }

        this.mapGrid[row][col] = {
          x: location.tile_reference.match(/^([A-Z]+)/)?.[1] || '',
          y: row + 1,
          symbol: symbol,
          type: 'city',
          data: location
        };
      }
    });
  }

  /**
   * Generate ASCII map representation
   */
  public generateMap(): string {
    this.placeCities();

    let mapString = '# 🗺️ uDOS World Map\n\n';
    mapString += `**Generated:** ${new Date().toISOString()}\n`;
    mapString += `**Resolution:** ${this.COLUMNS}×${this.ROWS} tiles\n`;
    mapString += `**Cities:** ${this.locationMap.length} locations\n\n`;

    // Column headers
    mapString += '```\n';
    mapString += '    ';
    for (let col = 0; col < this.COLUMNS; col++) {
      const header = this.numberToColumnId(col);
      mapString += header.padStart(2, ' ');
    }
    mapString += '\n';

    // Map rows
    for (let row = 0; row < this.ROWS; row++) {
      const rowNum = (row + 1).toString().padStart(2, '0');
      mapString += `${rowNum}  `;

      for (let col = 0; col < this.COLUMNS; col++) {
        mapString += this.mapGrid[row][col].symbol;
      }
      mapString += '\n';
    }

    mapString += '```\n\n';

    // Add legend
    mapString += this.generateLegend();

    return mapString;
  }

  /**
   * Generate map legend
   */
  private generateLegend(): string {
    let legend = '## 🎨 Map Legend\n\n';

    // City types
    legend += '### 🏙️ Locations\n';
    legend += '🏙️ Cities | ✈️ Airports | 🗿 World Wonders | 🏝️ Islands | ⛰️ Mountains\n\n';

    // Terrain types
    legend += '### 🌍 Terrain\n';
    this.terrainMap.forEach(terrain => {
      legend += `${terrain.symbol} ${terrain.name} - ${terrain.description}\n`;
    });

    legend += '\n### 🌊 Base Layer\n';
    legend += '🟦 Ocean - Default background terrain\n\n';

    return legend;
  }

  /**
   * Get city information at specific coordinates
   */
  public getCityAt(tileRef: string): LocationData | null {
    const coords = this.tileRefToCoords(tileRef);
    if (!coords) return null;

    const { col, row } = coords;
    const tile = this.mapGrid[row][col];

    return tile.type === 'city' ? tile.data : null;
  }

  /**
   * Generate filtered map by region
   */
  public generateRegionMap(region: string): string {
    const regionCities = this.locationMap.filter(loc =>
      loc.region.toLowerCase() === region.toLowerCase()
    );

    let mapString = `# 🗺️ ${region} Regional Map\n\n`;
    mapString += `**Cities in ${region}:** ${regionCities.length}\n\n`;

    regionCities.forEach(city => {
      mapString += `📍 **${city.city_name}** (${city.tile_reference}) - ${city.country}\n`;
    });

    return mapString;
  }

  /**
   * Save map to file
   */
  public saveMap(filename: string): void {
    const mapContent = this.generateMap();
    const outputPath = path.join(__dirname, '../output', filename);

    // Ensure output directory exists
    const outputDir = path.dirname(outputPath);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(outputPath, mapContent, 'utf8');
    console.log(`✅ Map saved to: ${outputPath}`);
  }
}

// CLI usage
if (require.main === module) {
  const generator = new MapGenerator();

  const args = process.argv.slice(2);
  const command = args[0] || 'generate';

  switch (command) {
    case 'generate':
      const filename = args[1] || 'world-map.md';
      generator.saveMap(filename);
      break;

    case 'region':
      const region = args[1] || 'Europe';
      console.log(generator.generateRegionMap(region));
      break;

    case 'city':
      const tileRef = args[1];
      if (tileRef) {
        const city = generator.getCityAt(tileRef);
        if (city) {
          console.log(`🏙️ ${city.city_name}, ${city.country}`);
          console.log(`📍 ${city.tile_reference} | 👥 ${city.population_tier}`);
        } else {
          console.log(`❌ No city found at ${tileRef}`);
        }
      }
      break;

    default:
      console.log('uDOS Map Generator v1.0.4.1');
      console.log('Usage:');
      console.log('  npm run map generate [filename]  - Generate world map');
      console.log('  npm run map region <region>      - Generate region map');
      console.log('  npm run map city <tile_ref>      - Get city info');
  }
}

export default MapGenerator;
