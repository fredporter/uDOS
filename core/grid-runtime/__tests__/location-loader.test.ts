/**
 * Tests for Location Loader (terrestrial + cosmic scales)
 */

import {
  World,
  loadLocationDatabase,
  DistanceScale,
  getDistanceScale,
  getDistanceUnit,
  getCellDistance,
} from '../src/location-loader';
import { LocationDatabase, Location } from '../src/location-types';

// Mock terrestrial location data
const mockTerrestrialData: LocationDatabase = {
  version: '1.0.7.0',
  locations: {
    'L300-AA10': {
      id: 'L300-AA10',
      layer: 300,
      center: 'AA10',
      metadata: {
        name: 'City Plaza',
        description: 'Central plaza with fountain',
        type: 'city',
        tags: ['urban', 'public'],
      },
      connections: [
        { target: 'L300-BD14', type: 'walk', bidirectional: true },
      ],
      tiles: {
        'AA10': {
          objects: [{ char: '⛲', label: 'Fountain', z: 0 }],
        },
      },
    },
    'L300-BD14': {
      id: 'L300-BD14',
      layer: 300,
      center: 'BD14',
      metadata: {
        name: 'Market District',
        description: 'Bustling marketplace',
        type: 'city',
        tags: ['urban', 'commerce'],
      },
      connections: [
        { target: 'L300-AA10', type: 'walk', bidirectional: true },
        { target: 'L301-BD14', type: 'stairs', label: 'Enter building', bidirectional: true },
      ],
      tiles: {
        'BD14': {
          sprites: [{ id: 'merchant', char: '🧙', label: 'Merchant', z: 1 }],
        },
      },
    },
    'L301-BD14': {
      id: 'L301-BD14',
      layer: 301,
      center: 'BD14',
      metadata: {
        name: 'Shop Interior',
        description: 'Inside the market shop',
        type: 'indoor',
      },
      connections: [
        { target: 'L300-BD14', type: 'stairs', label: 'Exit', bidirectional: true },
      ],
      tiles: {},
    },
  },
};

// Mock cosmic location data (use unique IDs from terrestrial)
const mockCosmicData: LocationDatabase = {
  version: '1.0.7.0',
  locations: {
    'L300-ZZ01': {
      id: 'L300-ZZ01',
      layer: 300,
      center: 'ZZ01',
      metadata: {
        name: 'Earth Surface',
        description: 'Home planet surface',
        type: 'terrestrial',
        tags: ['earth', 'surface'],
      },
      connections: [
        { target: 'L306-ZZ01', type: 'teleport', label: 'Launch to orbit' },
      ],
      tiles: {},
    },
    'L306-ZZ01': {
      id: 'L306-ZZ01',
      layer: 306,
      center: 'ZZ01',
      metadata: {
        name: 'LEO Station',
        description: 'Low Earth Orbit space station',
        type: 'orbital',
        tags: ['space', 'station'],
      },
      connections: [
        { target: 'L300-ZZ01', type: 'teleport', label: 'Return to Earth' },
        { target: 'L311-BB12', type: 'jump', label: 'Jump to Mars' },
      ],
      tiles: {},
    },
    'L311-BB12': {
      id: 'L311-BB12',
      layer: 311,
      center: 'BB12',
      metadata: {
        name: 'Mars Colony',
        description: 'Red planet settlement',
        type: 'planetary',
        tags: ['mars', 'colony'],
      },
      connections: [
        { target: 'L306-ZZ01', type: 'jump', label: 'Return to Earth orbit' },
        { target: 'L321-CC15', type: 'teleport', label: 'Warp to Alpha Centauri' },
      ],
      tiles: {},
    },
    'L321-CC15': {
      id: 'L321-CC15',
      layer: 321,
      center: 'CC15',
      metadata: {
        name: 'Alpha Centauri',
        description: 'Nearest star system',
        type: 'stellar',
        tags: ['star', 'system'],
      },
      connections: [
        { target: 'L311-BB12', type: 'teleport', label: 'Warp to Sol system' },
      ],
      tiles: {},
    },
  },
};

describe('Location Loader', () => {
  
  describe('Distance Scales', () => {
    it('should identify terrestrial scale (L300-L305)', () => {
      expect(getDistanceScale(300)).toBe(DistanceScale.TERRESTRIAL);
      expect(getDistanceScale(305)).toBe(DistanceScale.TERRESTRIAL);
    });
    
    it('should identify orbital scale (L306-L310)', () => {
      expect(getDistanceScale(306)).toBe(DistanceScale.ORBITAL);
      expect(getDistanceScale(310)).toBe(DistanceScale.ORBITAL);
    });
    
    it('should identify planetary scale (L311-L320)', () => {
      expect(getDistanceScale(311)).toBe(DistanceScale.PLANETARY);
      expect(getDistanceScale(320)).toBe(DistanceScale.PLANETARY);
    });
    
    it('should identify stellar scale (L321-L350)', () => {
      expect(getDistanceScale(321)).toBe(DistanceScale.STELLAR);
      expect(getDistanceScale(350)).toBe(DistanceScale.STELLAR);
    });
    
    it('should identify galactic scale (L351-L400)', () => {
      expect(getDistanceScale(351)).toBe(DistanceScale.GALACTIC);
      expect(getDistanceScale(400)).toBe(DistanceScale.GALACTIC);
    });
    
    it('should identify cosmic scale (L401+)', () => {
      expect(getDistanceScale(401)).toBe(DistanceScale.COSMIC);
      expect(getDistanceScale(999)).toBe(DistanceScale.COSMIC);
    });
    
    it('should provide correct distance units', () => {
      expect(getDistanceUnit(DistanceScale.TERRESTRIAL)).toBe('m');
      expect(getDistanceUnit(DistanceScale.ORBITAL)).toBe('km');
      expect(getDistanceUnit(DistanceScale.PLANETARY)).toBe('AU');
      expect(getDistanceUnit(DistanceScale.STELLAR)).toBe('ly');
      expect(getDistanceUnit(DistanceScale.GALACTIC)).toBe('kly');
      expect(getDistanceUnit(DistanceScale.COSMIC)).toBe('Mly');
    });
    
    it('should provide cell distance for each scale', () => {
      expect(getCellDistance(DistanceScale.TERRESTRIAL)).toBe(16); // meters
      expect(getCellDistance(DistanceScale.ORBITAL)).toBe(1000); // km
      expect(getCellDistance(DistanceScale.PLANETARY)).toBe(0.1); // AU
      expect(getCellDistance(DistanceScale.STELLAR)).toBe(1); // ly
      expect(getCellDistance(DistanceScale.GALACTIC)).toBe(100); // kly
      expect(getCellDistance(DistanceScale.COSMIC)).toBe(1000); // Mly
    });
  });
  
  describe('World - Terrestrial Locations', () => {
    let world: World;
    
    beforeEach(() => {
      world = loadLocationDatabase(mockTerrestrialData);
    });
    
    it('should load all locations', () => {
      expect(world.getAllLocations().length).toBe(3);
    });
    
    it('should get location by ID', () => {
      const location = world.getLocation('L300-AA10');
      expect(location).toBeDefined();
      expect(location!.metadata.name).toBe('City Plaza');
    });
    
    it('should get locations by layer', () => {
      const layer300 = world.getLocationsByLayer(300);
      expect(layer300.length).toBe(2);
      
      const layer301 = world.getLocationsByLayer(301);
      expect(layer301.length).toBe(1);
    });
    
    it('should get tile content', () => {
      const tile = world.getTileContent('L300-AA10', 'AA10');
      expect(tile).toBeDefined();
      expect(tile!.objects![0].label).toBe('Fountain');
    });
    
    it('should get connected locations', () => {
      const connections = world.getConnectedLocations('L300-AA10');
      expect(connections).toContain('L300-BD14');
      
      // Bidirectional connection
      const reverse = world.getConnectedLocations('L300-BD14');
      expect(reverse).toContain('L300-AA10');
    });
    
    it('should find shortest path between locations', () => {
      const path = world.findPath('L300-AA10', 'L301-BD14');
      expect(path).toEqual(['L300-AA10', 'L300-BD14', 'L301-BD14']);
    });
    
    it('should return null for unreachable locations', () => {
      // Create isolated world
      const isolatedWorld = new World();
      isolatedWorld.loadDatabase({
        version: '1.0.7.0',
        locations: {
          'L300-AA10': {
            id: 'L300-AA10',
            layer: 300,
            center: 'AA10',
            metadata: { name: 'Isolated', description: 'No connections', type: 'island' },
            connections: [],
            tiles: {},
          },
          'L300-ZZ99': {
            id: 'L300-ZZ99',
            layer: 300,
            center: 'ZZ99',
            metadata: { name: 'Remote', description: 'Also isolated', type: 'island' },
            connections: [],
            tiles: {},
          },
        },
      });
      
      const path = isolatedWorld.findPath('L300-AA10', 'L300-ZZ99');
      expect(path).toBeNull();
    });
    
    it('should search locations by name', () => {
      const results = world.searchLocations('Market District');
      expect(results.length).toBeGreaterThanOrEqual(1);
      expect(results.some(r => r.id === 'L300-BD14')).toBe(true);
    });
    
    it('should search locations by tags', () => {
      const results = world.searchLocations('urban');
      expect(results.length).toBe(2);
    });
    
    it('should get location info', () => {
      const info = world.getLocationInfo('L300-AA10');
      expect(info).toBeDefined();
      expect(info!.name).toBe('City Plaza');
      expect(info!.scale).toBe(DistanceScale.TERRESTRIAL);
      expect(info!.unit).toBe('m');
      expect(info!.connectionCount).toBe(1);
    });
    
    it('should calculate world statistics', () => {
      const stats = world.getStatistics();
      expect(stats.totalLocations).toBe(3);
      expect(stats.locationsByScale[DistanceScale.TERRESTRIAL]).toBe(3);
      expect(stats.totalConnections).toBe(4); // 2 bidirectional = 4 total
    });
  });
  
  describe('World - Cosmic Locations', () => {
    let world: World;
    
    beforeEach(() => {
      world = loadLocationDatabase(mockCosmicData);
    });
    
    it('should load multi-scale locations', () => {
      expect(world.getAllLocations().length).toBe(4);
    });
    
    it('should get locations by scale', () => {
      const terrestrial = world.getLocationsByScale(DistanceScale.TERRESTRIAL);
      expect(terrestrial.length).toBe(1);
      
      const orbital = world.getLocationsByScale(DistanceScale.ORBITAL);
      expect(orbital.length).toBe(1);
      
      const planetary = world.getLocationsByScale(DistanceScale.PLANETARY);
      expect(planetary.length).toBe(1);
      
      const stellar = world.getLocationsByScale(DistanceScale.STELLAR);
      expect(stellar.length).toBe(1);
    });
    
    it('should handle cross-scale connections', () => {
      const path = world.findPath('L300-ZZ01', 'L321-CC15');
      expect(path).toBeDefined();
      expect(path!.length).toBe(4);
      expect(path).toEqual([
        'L300-ZZ01',
        'L306-ZZ01',
        'L311-BB12',
        'L321-CC15',
      ]);
    });
    
    it('should track statistics across scales', () => {
      const stats = world.getStatistics();
      expect(stats.totalLocations).toBe(4);
      expect(stats.locationsByScale[DistanceScale.TERRESTRIAL]).toBe(1);
      expect(stats.locationsByScale[DistanceScale.ORBITAL]).toBe(1);
      expect(stats.locationsByScale[DistanceScale.PLANETARY]).toBe(1);
      expect(stats.locationsByScale[DistanceScale.STELLAR]).toBe(1);
    });
    
    it('should search across all scales', () => {
      const results = world.searchLocations('colony');
      expect(results.length).toBe(1);
      expect(results[0].layer).toBe(311); // Mars Colony
    });
  });
  
  describe('Edge Cases', () => {
    it('should handle empty database', () => {
      const world = loadLocationDatabase({
        version: '1.0.7.0',
        locations: {},
      });
      
      expect(world.getAllLocations().length).toBe(0);
      expect(world.getStatistics().totalLocations).toBe(0);
    });
    
    it('should handle missing location gracefully', () => {
      const world = loadLocationDatabase(mockTerrestrialData);
      const missing = world.getLocation('L999-XX99');
      expect(missing).toBeUndefined();
    });
    
    it('should handle path to same location', () => {
      const world = loadLocationDatabase(mockTerrestrialData);
      const path = world.findPath('L300-AA10', 'L300-AA10');
      expect(path).toEqual(['L300-AA10']);
    });
  });
  
});
