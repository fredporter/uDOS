import { renderGrid, GridRendererInput, Canvas80x30 } from "./index.js";

export interface TestResult {
  name: string;
  passed: boolean;
  message: string;
}

const results: TestResult[] = [];

function assert(condition: boolean, message: string) {
  if (!condition) {
    throw new Error(`Assertion failed: ${message}`);
  }
}

// Test 1: Canvas dimensions and clearing
function testCanvasDimensions(): TestResult {
  try {
    const c = new Canvas80x30();
    const lines = c.toLines();

    assert(lines.length === 30, `Expected 30 lines, got ${lines.length}`);
    assert(
      lines[0].length === 80,
      `Expected 80 chars per line, got ${lines[0].length}`,
    );

    return {
      name: "Canvas Dimensions",
      passed: true,
      message: "Canvas is 80x30",
    };
  } catch (e: any) {
    return { name: "Canvas Dimensions", passed: false, message: e.message };
  }
}

// Test 2: Box drawing
function testBoxDrawing(): TestResult {
  try {
    const c = new Canvas80x30();
    c.box(0, 0, 10, 5, "single", "Test");
    const lines = c.toLines();

    assert(lines[0][0] === "+", "Top-left corner should be +");
    assert(lines[0][9] === "+", "Top-right corner should be +");
    assert(lines[4][0] === "+", "Bottom-left corner should be +");
    assert(lines[4][9] === "+", "Bottom-right corner should be +");
    assert(lines[0].includes("Test"), "Title should appear in box");

    return {
      name: "Box Drawing",
      passed: true,
      message: "Boxes render correctly",
    };
  } catch (e: any) {
    return { name: "Box Drawing", passed: false, message: e.message };
  }
}

// Test 3: Text rendering
function testTextRendering(): TestResult {
  try {
    const c = new Canvas80x30();
    c.text(0, 0, 80, 5, "Hello World", { wrap: false });
    const lines = c.toLines();

    assert(lines[0].includes("Hello World"), "Text should appear on canvas");

    return {
      name: "Text Rendering",
      passed: true,
      message: "Text renders correctly",
    };
  } catch (e: any) {
    return { name: "Text Rendering", passed: false, message: e.message };
  }
}

// Test 4: Table rendering
function testTableRendering(): TestResult {
  try {
    const c = new Canvas80x30();
    c.table(
      0,
      0,
      40,
      10,
      [
        { key: "id", title: "ID" },
        { key: "val", title: "Value" },
      ],
      [
        { id: "1", val: "100" },
        { id: "2", val: "200" },
      ],
      { header: true },
    );

    const lines = c.toLines();
    const tableText = lines.slice(0, 10).join("\n");

    assert(tableText.includes("ID"), "Header 'ID' should appear");
    assert(tableText.includes("Value"), "Header 'Value' should appear");
    assert(tableText.includes("100"), "Data '100' should appear");

    return {
      name: "Table Rendering",
      passed: true,
      message: "Tables render with headers and data",
    };
  } catch (e: any) {
    return { name: "Table Rendering", passed: false, message: e.message };
  }
}

// Test 5: Calendar mode rendering
function testCalendarMode(): TestResult {
  try {
    const input: GridRendererInput = {
      mode: "calendar",
      spec: { width: 80, height: 30, title: "Test Calendar" },
      data: {
        events: [{ time: "10:00", title: "Meeting" }],
        tasks: [{ status: "[ ]", text: "Task 1" }],
      },
    };

    const result = renderGrid(input);

    assert(
      result.lines.length === 30,
      `Expected 30 lines, got ${result.lines.length}`,
    );
    assert(
      result.rawText.includes("udos-grid:v1"),
      "Should include format marker",
    );
    assert(result.rawText.includes("Test Calendar"), "Should include title");

    return {
      name: "Calendar Mode",
      passed: true,
      message: "Calendar mode renders correctly",
    };
  } catch (e: any) {
    return { name: "Calendar Mode", passed: false, message: e.message };
  }
}

// Test 6: Table mode rendering
function testTableMode(): TestResult {
  try {
    const input: GridRendererInput = {
      mode: "table",
      spec: { width: 80, height: 30, title: "Test Table" },
      data: {
        query: "SELECT * FROM test",
        columns: [{ key: "id", title: "ID" }],
        rows: [{ id: "1" }],
      },
    };

    const result = renderGrid(input);

    assert(result.lines.length === 30, "Should have 30 lines");
    assert(result.rawText.includes("Table"), "Should include Table in output");
    assert(result.rawText.includes("Rows:"), "Should show row count");

    return {
      name: "Table Mode",
      passed: true,
      message: "Table mode renders correctly",
    };
  } catch (e: any) {
    return { name: "Table Mode", passed: false, message: e.message };
  }
}

// Test 7: Schedule mode rendering
function testScheduleMode(): TestResult {
  try {
    const input: GridRendererInput = {
      mode: "schedule",
      spec: { width: 80, height: 30, title: "Test Schedule" },
      data: {
        events: [{ time: "10:00", item: "Meeting", location: "Room A" }],
      },
    };

    const result = renderGrid(input);

    assert(result.lines.length === 30, "Should have 30 lines");
    assert(result.rawText.includes("Schedule"), "Should include Schedule");

    return {
      name: "Schedule Mode",
      passed: true,
      message: "Schedule mode renders correctly",
    };
  } catch (e: any) {
    return { name: "Schedule Mode", passed: false, message: e.message };
  }
}

// Test 8: Map mode rendering with LocId overlays
function testMapMode(): TestResult {
  try {
    const input: GridRendererInput = {
      mode: "map",
      spec: { width: 80, height: 30, title: "Test Map" },
      data: {
        focusLocId: "EARTH:SUR:L305-DA11",
        overlays: [
          { locId: "EARTH:SUR:L305-DA11", icon: "T", label: "Tasks" },
          { locId: "EARTH:SUR:L305-DA12", icon: "N", label: "Notes" },
        ],
      },
    };

    const result = renderGrid(input);

    assert(result.lines.length === 30, "Should have 30 lines");
    assert(
      result.rawText.includes("EARTH:SUR:L305-DA11"),
      "Should include focus LocId",
    );
    assert(result.rawText.includes("Legend"), "Should include legend");
    assert(result.rawText.includes("T = Tasks"), "Should map T icon");
    assert(result.rawText.includes("N = Notes"), "Should map N icon");

    return {
      name: "Map Mode",
      passed: true,
      message: "Map mode with LocId overlays renders correctly",
    };
  } catch (e: any) {
    return { name: "Map Mode", passed: false, message: e.message };
  }
}

// Test 9: Dashboard mode rendering
function testDashboardMode(): TestResult {
  try {
    const input: GridRendererInput = {
      mode: "dashboard",
      spec: { width: 80, height: 30, title: "Test Dashboard" },
      data: {
        missions: [{ status: "✓", title: "Task 1" }],
        stats: { CPU: "50%" },
        logs: [{ time: "12:00", level: "INFO", message: "Test" }],
      },
    };

    const result = renderGrid(input);

    assert(result.lines.length === 30, "Should have 30 lines");
    assert(result.rawText.includes("Dashboard"), "Should include Dashboard");

    return {
      name: "Dashboard Mode",
      passed: true,
      message: "Dashboard mode renders correctly",
    };
  } catch (e: any) {
    return { name: "Dashboard Mode", passed: false, message: e.message };
  }
}

// Test 10: Z-aware map viewport behavior
function testMapModeZViewport(): TestResult {
  try {
    const input: GridRendererInput = {
      mode: "map",
      spec: { width: 80, height: 30, title: "Z Viewport Map" },
      data: {
        focusLocId: "EARTH:SUR:L305-DA11-Z2",
        viewport: { zRange: 1 },
        overlays: [
          { locId: "EARTH:SUR:L305-DA11-Z2", icon: "T", label: "Focus Layer" },
          { locId: "EARTH:SUR:L305-DA12-Z3", icon: "N", label: "Nearby Layer" },
          { locId: "EARTH:SUR:L305-DA13-Z7", icon: "E", label: "Far Layer" },
        ],
      },
    };

    const result = renderGrid(input);

    assert(result.lines.length === 30, "Should have 30 lines");
    assert(result.rawText.includes("Z Viewport"), "Should include z viewport panel");
    assert(result.rawText.includes("Focus: z=2"), "Should show focus z plane");
    assert(result.rawText.includes("Range: +/-1"), "Should show z range");
    assert(result.rawText.includes("Hidden: 1"), "Should count hidden far overlays");
    assert(!result.rawText.includes("Events: 1"), "Far overlay should not count in visible stats");

    return {
      name: "Map Mode Z Viewport",
      passed: true,
      message: "Map mode filters overlays by z viewport correctly",
    };
  } catch (e: any) {
    return { name: "Map Mode Z Viewport", passed: false, message: e.message };
  }
}

// Test 11: Output format compliance
function testOutputFormat(): TestResult {
  try {
    const input: GridRendererInput = {
      mode: "calendar",
      spec: {
        width: 80,
        height: 30,
        title: "Format Test",
        theme: "mono",
        ts: "2026-02-05T10:00:00Z",
      },
      data: { events: [], tasks: [] },
    };

    const result = renderGrid(input);

    assert(
      result.rawText.startsWith("--- udos-grid:v1"),
      "Should start with format marker",
    );
    assert(
      result.rawText.includes("--- end ---"),
      "Should end with terminator",
    );
    assert(
      result.lines.every((l: string) => l.length === 80),
      "All lines should be exactly 80 chars",
    );

    return {
      name: "Output Format",
      passed: true,
      message: "Output format is compliant",
    };
  } catch (e: any) {
    return { name: "Output Format", passed: false, message: e.message };
  }
}

// Run all tests
export function runTests(): TestResult[] {
  const tests = [
    testCanvasDimensions,
    testBoxDrawing,
    testTextRendering,
    testTableRendering,
    testCalendarMode,
    testTableMode,
    testScheduleMode,
    testMapMode,
    testDashboardMode,
    testMapModeZViewport,
    testOutputFormat,
  ];

  results.length = 0;
  for (const test of tests) {
    results.push(test());
  }

  return results;
}

// Print results
export function printResults(results: TestResult[]) {
  console.log("=== UGRID CORE TEST RESULTS ===\n");

  let passed = 0;
  let failed = 0;

  for (const result of results) {
    const status = result.passed ? "✓ PASS" : "✗ FAIL";
    console.log(`${status} | ${result.name}`);
    console.log(`       ${result.message}\n`);

    if (result.passed) passed++;
    else failed++;
  }

  console.log(`\nTotal: ${passed}/${results.length} passed`);
  console.log(
    `Status: ${failed === 0 ? "ALL TESTS PASSED ✓" : `${failed} TESTS FAILED`}`,
  );

  return failed === 0;
}

// Main
if (typeof require !== "undefined" && require.main === module) {
  const testResults = runTests();
  const allPassed = printResults(testResults);
  process.exit(allPassed ? 0 : 1);
}
