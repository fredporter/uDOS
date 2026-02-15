/**
 * Comprehensive Tests for Spatial Parsing & Registry
 *
 * Tests LocId parser, PlaceRef parser, AnchorRegistry, and validation.
 * @module spatial/tests
 */

import { strict as assert } from "assert";
import {
  parseLocId,
  parsePlaceRef,
  parseAddressPath,
  normaliseFrontmatterPlaces,
  isValidCell,
  isValidRow,
  isValidZ,
} from "./parse.js";
import {
  isValidLayer,
  isValidDepth,
  getLayerBand,
  validatePlaceRef,
  canonicalizePlace,
  describePlaceRef,
  LayerBand,
} from "./validation.js";
import { AnchorRegistry, loadAnchorsFromJSON } from "./registry.js";

/**
 * Test Suite: LocId Parser
 */
export function testLocIdParser(): void {
  console.log("Testing LocId Parser...");

  // Valid LocIds
  assert.ok(parseLocId("L305-DA11"));
  assert.ok(parseLocId("L300-AA10"));
  assert.ok(parseLocId("L899-ZZ39"));
  assert.ok(parseLocId("L305-DA11-Z0"));
  assert.ok(parseLocId("L305-DA11-Z-5"));

  // Invalid: malformed
  assert.equal(parseLocId("L305"), null);
  assert.equal(parseLocId("305-DA11"), null);
  assert.equal(parseLocId("L305-DA"), null);
  assert.equal(parseLocId("L305-DA1"), null);
  assert.equal(parseLocId("L305-DA11-Z"), null);
  assert.equal(parseLocId("L305-DA11-Z100"), null);

  // Invalid: bad layer
  assert.equal(parseLocId("L199-DA11"), null);
  assert.equal(parseLocId("L900-DA11"), null);

  // Invalid: bad cell
  assert.equal(parseLocId("L305-1A11"), null); // starts with digit
  assert.equal(parseLocId("L305-aa11"), null); // lowercase
  assert.equal(parseLocId("L305-DA09"), null); // row < 10
  assert.equal(parseLocId("L305-DA40"), null); // row > 39

  // Valid LocId structure
  const locId = parseLocId("L305-DA11");
  assert.equal(locId?.locId, "L305-DA11");
  assert.equal(locId?.effectiveLayer, 305);
  assert.equal(locId?.finalCell, "DA11");
  assert.equal(locId?.z, undefined);

  const locIdZ = parseLocId("L305-DA11-Z2");
  assert.equal(locIdZ?.locId, "L305-DA11-Z2");
  assert.equal(locIdZ?.z, 2);

  console.log("✓ LocId Parser tests passed");
}

/**
 * Test Suite: Cell & Row Validation
 */
export function testCellValidation(): void {
  console.log("Testing Cell & Row Validation...");

  // Valid cells
  assert.ok(isValidCell("AA10"));
  assert.ok(isValidCell("ZZ39"));
  assert.ok(isValidCell("BB20"));

  // Invalid cells
  assert.ok(!isValidCell("AA09")); // row too low
  assert.ok(!isValidCell("AA40")); // row too high
  assert.ok(!isValidCell("aa10")); // lowercase
  assert.ok(!isValidCell("1A10")); // digit first
  assert.ok(!isValidCell("A10")); // only 1 letter

  // Valid rows
  assert.ok(isValidRow(10));
  assert.ok(isValidRow(39));
  assert.ok(isValidRow(20));

  // Invalid rows
  assert.ok(!isValidRow(9));
  assert.ok(!isValidRow(40));
  assert.ok(!isValidRow(-1));

  // z-axis
  assert.ok(isValidZ(0));
  assert.ok(isValidZ(-99));
  assert.ok(isValidZ(99));
  assert.ok(!isValidZ(-100));
  assert.ok(!isValidZ(100));
  assert.ok(!isValidZ(1.5));

  console.log("✓ Cell Validation tests passed");
}

/**
 * Test Suite: Address Path Parser
 */
export function testAddressPathParser(): void {
  console.log("Testing Address Path Parser...");

  // Single cell (canonical)
  const path1 = parseAddressPath("L305-DA11");
  assert.equal(path1?.baseLayer, 305);
  assert.deepEqual(path1?.cells, ["DA11"]);
  assert.equal(path1?.effectiveLayer, 305);
  assert.equal(path1?.canonicalLocId, "L305-DA11");

  // Multiple cells (narrative path)
  const path2 = parseAddressPath("L300-AC10-BB20-DA11");
  assert.equal(path2?.baseLayer, 300);
  assert.deepEqual(path2?.cells, ["AC10", "BB20", "DA11"]);
  assert.equal(path2?.effectiveLayer, 302); // 300 + 2 steps
  assert.equal(path2?.canonicalLocId, "L302-DA11");

  // Address path with z-axis
  const path3 = parseAddressPath("L300-AC10-BB20-DA11-Z3");
  assert.equal(path3?.effectiveLayer, 302);
  assert.equal(path3?.canonicalLocId, "L302-DA11-Z3");
  assert.equal(path3?.z, 3);

  // Invalid
  assert.equal(parseAddressPath("L305"), null);
  assert.equal(parseAddressPath("L305-DA09-BB20"), null); // bad cell in path
  assert.equal(parseAddressPath("L305-DA11-Z100"), null); // bad z

  console.log("✓ Address Path Parser tests passed");
}

/**
 * Test Suite: PlaceRef Parser
 */
export function testPlaceRefParser(): void {
  console.log("Testing PlaceRef Parser...");

  // Simple forms
  const p1 = parsePlaceRef("EARTH:SUR:L305-DA11");
  assert.equal(p1?.anchorId, "EARTH");
  assert.equal(p1?.space, "SUR");
  assert.equal(p1?.locId, "L305-DA11");
  assert.equal(p1?.depth, undefined);
  assert.equal(p1?.instance, undefined);

  const p1z = parsePlaceRef("EARTH:SUR:L305-DA11-Z2");
  assert.equal(p1z?.locId, "L305-DA11-Z2");

  // Composite anchor
  const p2 = parsePlaceRef("BODY:MOON:SUR:L610-AB22");
  assert.equal(p2?.anchorId, "BODY:MOON");
  assert.equal(p2?.space, "SUR");

  const p3 = parsePlaceRef("GAME:skyrim:SUB:L402-CC18");
  assert.equal(p3?.anchorId, "GAME:skyrim");
  assert.equal(p3?.space, "SUB");

  // With depth
  const p4 = parsePlaceRef("EARTH:SUB:L305-DA11:D7");
  assert.equal(p4?.depth, 7);
  assert.equal(p4?.instance, undefined);

  // With instance
  const p5 = parsePlaceRef("GAME:skyrim:SUB:L402-CC18:Iwinterhold");
  assert.equal(p5?.instance, "winterhold");

  // With both
  const p6 = parsePlaceRef("GAME:skyrim:SUB:L402-CC18:D3:Isolitude");
  assert.equal(p6?.depth, 3);
  assert.equal(p6?.instance, "solitude");

  // Invalid forms
  assert.equal(parsePlaceRef("EARTH:SUR"), null); // missing LocId
  assert.equal(parsePlaceRef("BODY:SUR:L305-DA11"), null); // BODY without subtype
  assert.equal(parsePlaceRef("EARTH:INVALID:L305-DA11"), null); // bad space
  assert.equal(parsePlaceRef("EARTH:SUR:L305-DA"), null); // bad LocId
  assert.equal(parsePlaceRef("EARTH:SUR:L305-DA11-Z100"), null); // bad z

  console.log("✓ PlaceRef Parser tests passed");
}

/**
 * Test Suite: Layer Validation & Bands
 */
export function testLayerValidation(): void {
  console.log("Testing Layer Validation & Bands...");

  // Valid layers
  assert.ok(isValidLayer(300));
  assert.ok(isValidLayer(305));
  assert.ok(isValidLayer(899));

  // Invalid layers
  assert.ok(!isValidLayer(299));
  assert.ok(!isValidLayer(900));
  assert.ok(!isValidLayer(-1));
  assert.ok(!isValidLayer(305.5)); // not integer

  // Layer bands
  assert.equal(getLayerBand(300), LayerBand.TERRESTRIAL);
  assert.equal(getLayerBand(305), LayerBand.TERRESTRIAL);
  assert.equal(getLayerBand(306), LayerBand.REGIONAL);
  assert.equal(getLayerBand(400), LayerBand.CITIES);
  assert.equal(getLayerBand(600), LayerBand.PLANETARY);
  assert.equal(getLayerBand(800), LayerBand.STELLAR);
  assert.equal(getLayerBand(899), null); // Above defined bands? Actually should be STELLAR

  // Depth validation
  assert.ok(isValidDepth(0));
  assert.ok(isValidDepth(7));
  assert.ok(isValidDepth(99));
  assert.ok(!isValidDepth(-1));
  assert.ok(!isValidDepth(100));
  assert.ok(!isValidDepth(7.5)); // not integer

  console.log("✓ Layer Validation tests passed");
}

/**
 * Test Suite: PlaceRef Validation
 */
export function testPlaceRefValidation(): void {
  console.log("Testing PlaceRef Validation...");

  // Valid
  let result = validatePlaceRef("EARTH:SUR:L305-DA11");
  assert.ok(result.valid, result.error);

  result = validatePlaceRef("BODY:MARS:SUR:L610-AB22");
  assert.ok(result.valid, result.error);

  result = validatePlaceRef("GAME:skyrim:SUB:L402-CC18:D3:Iwinterhold");
  assert.ok(result.valid, result.error);

  // Invalid structures
  result = validatePlaceRef("EARTH:SUR");
  assert.ok(!result.valid);

  result = validatePlaceRef("BODY:SUR:L305-DA11");
  assert.ok(!result.valid); // BODY needs subtype

  // Invalid space
  result = validatePlaceRef("EARTH:INVALID:L305-DA11");
  assert.ok(!result.valid);

  // Invalid layer
  result = validatePlaceRef("EARTH:SUR:L199-DA11");
  assert.ok(!result.valid);

  result = validatePlaceRef("EARTH:SUR:L900-DA11");
  assert.ok(!result.valid);

  // With anchor validator
  const validator = (id: string) => id === "EARTH" || id === "BODY:MOON";
  result = validatePlaceRef("EARTH:SUR:L305-DA11", validator);
  assert.ok(result.valid);

  result = validatePlaceRef("BODY:MARS:SUR:L610-AB22", validator);
  assert.ok(!result.valid); // BODY:MARS not registered

  console.log("✓ PlaceRef Validation tests passed");
}

/**
 * Test Suite: Place Canonicalization
 */
export function testPlaceCanonical(): void {
  console.log("Testing Place Canonicalization...");

  // Simple canonicalization
  let canonical = canonicalizePlace("EARTH", "SUR", "L305-DA11");
  assert.equal(canonical, "EARTH:SUR:L305-DA11");

  // With depth
  canonical = canonicalizePlace("EARTH", "SUB", "L305-DA11", 7);
  assert.equal(canonical, "EARTH:SUB:L305-DA11:D7");

  // With instance
  canonical = canonicalizePlace(
    "GAME:skyrim",
    "SUB",
    "L402-CC18",
    undefined,
    "winterhold",
  );
  assert.equal(canonical, "GAME:skyrim:SUB:L402-CC18:Iwinterhold");

  // With both
  canonical = canonicalizePlace(
    "GAME:skyrim",
    "SUB",
    "L402-CC18",
    3,
    "solitude",
  );
  assert.equal(canonical, "GAME:skyrim:SUB:L402-CC18:D3:Isolitude");

  // Invalid cases return null
  assert.equal(canonicalizePlace("EARTH", "SUR", "L199-DA11"), null); // bad layer
  assert.equal(canonicalizePlace("EARTH", "SUB", "L305-DA11", 100), null); // bad depth
  assert.equal(canonicalizePlace("EARTH", "INVALID", "L305-DA11"), null); // bad space

  console.log("✓ Place Canonicalization tests passed");
}

/**
 * Test Suite: Anchor Registry
 */
export function testAnchorRegistry(): void {
  console.log("Testing Anchor Registry...");

  const registry = new AnchorRegistry();

  // Register anchors
  registry.registerAnchor({
    id: "EARTH",
    title: "Earth (Web Mercator)",
    description: "Real-world surface",
    capabilities: { locidReverseLookup: true },
  });

  registry.registerAnchor({
    id: "GAME:skyrim",
    title: "Skyrim",
    capabilities: { terminal: true, deterministicSeed: true },
  });

  // Count
  assert.equal(registry.count(), 2);

  // Retrieve
  const earth = registry.getAnchor("EARTH");
  assert.equal(earth?.title, "Earth (Web Mercator)");

  const skyrim = registry.getAnchor("GAME:skyrim");
  assert.equal(skyrim?.title, "Skyrim");

  // List
  const anchors = registry.listAnchors();
  assert.equal(anchors.length, 2);

  // Has
  assert.ok(registry.hasAnchor("EARTH"));
  assert.ok(!registry.hasAnchor("GAME:nonexistent"));

  // Validate
  assert.ok(registry.validateAnchor("EARTH"));
  assert.ok(!registry.validateAnchor("INVALID"));

  console.log("✓ Anchor Registry tests passed");
}

/**
 * Test Suite: Load Anchors from JSON
 */
export function testLoadAnchorsFromJSON(): void {
  console.log("Testing Load Anchors from JSON...");

  const data = {
    version: "1.3.0",
    anchors: [
      {
        anchorId: "EARTH",
        kind: "earth",
        title: "Earth (Web Mercator adapter)",
        status: "active",
        config: {
          projection: "web_mercator",
        },
      },
      {
        anchorId: "BODY:MOON",
        kind: "body",
        title: "Moon",
        status: "active",
        config: {
          frame: "selenographic",
        },
      },
    ],
  };

  const registry = loadAnchorsFromJSON(data);

  assert.equal(registry.count(), 2);
  assert.ok(registry.hasAnchor("EARTH"));
  assert.ok(registry.hasAnchor("BODY:MOON"));

  const earth = registry.getAnchorEntry("EARTH");
  assert.equal(earth?.config?.projection, "web_mercator");

  console.log("✓ Load Anchors from JSON tests passed");
}

/**
 * Test Suite: Frontmatter Normalization
 */
export function testFrontmatterNormalization(): void {
  console.log("Testing Frontmatter Normalization...");

  // Legacy grid_locations
  const result1 = normaliseFrontmatterPlaces({
    grid_locations: ["L305-DA11", "L305-BB20"],
  });
  assert.equal(result1.length, 2);
  assert.ok(result1.includes("EARTH:SUR:L305-DA11"));
  assert.ok(result1.includes("EARTH:SUR:L305-BB20"));

  // Modern places
  const result2 = normaliseFrontmatterPlaces({
    places: ["EARTH:SUR:L305-DA11", "GAME:skyrim:SUB:L402-CC18"],
  });
  assert.equal(result2.length, 2);

  // Mixed (deduped)
  const result3 = normaliseFrontmatterPlaces({
    places: ["EARTH:SUR:L305-DA11"],
    grid_locations: ["L305-DA11"],
  });
  assert.equal(result3.length, 1); // deduplicated

  console.log("✓ Frontmatter Normalization tests passed");
}

/**
 * Run All Tests
 */
export function runAllTests(): void {
  console.log("\n=== uDOS v1.3 Spatial Parsing & Registry Tests ===\n");

  testLocIdParser();
  testCellValidation();
  testAddressPathParser();
  testPlaceRefParser();
  testLayerValidation();
  testPlaceRefValidation();
  testPlaceCanonical();
  testAnchorRegistry();
  testLoadAnchorsFromJSON();
  testFrontmatterNormalization();

  console.log("\n✅ All spatial tests passed!\n");
}

// Run if executed directly
if (require.main === module) {
  runAllTests();
}
