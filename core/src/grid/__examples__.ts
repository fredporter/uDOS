import {
  renderGrid,
  GridRendererInput,
  Canvas80x30,
  LocIdOverlay,
} from "./index.js";

// Example 1: Calendar Day Mode
const calendarExample = (): string => {
  const input: GridRendererInput = {
    mode: "calendar",
    spec: {
      width: 80,
      height: 30,
      title: "Boss — Tue 3 Feb 2026",
      theme: "mono",
      ts: "2026-02-03T19:14:00+10:00",
    },
    data: {
      events: [
        { time: "09:00", title: "Standup" },
        { time: "10:00", title: "Build v1.3 grid renderer" },
        { time: "11:00", title: "Review themes" },
        { time: "12:00", title: "Lunch" },
        { time: "13:00", title: "Focus: Typo editor" },
        { time: "14:00", title: "Beacon testing" },
      ],
      tasks: [
        { status: "[ ]", text: "Wire vault picker" },
        { status: "[ ]", text: "Index tasks → sqlite" },
        { status: "[x]", text: "Add spatial schema" },
        { status: "[ ]", text: "Export _site (prose)" },
      ],
    },
  };
  return renderGrid(input).rawText;
};

// Example 2: Table Mode
const tableExample = (): string => {
  const input: GridRendererInput = {
    mode: "table",
    spec: {
      width: 80,
      height: 30,
      title: "Database Query Results",
      theme: "mono",
    },
    data: {
      query: "SELECT * FROM places LIMIT 20",
      columns: [
        { key: "id", title: "ID", width: 8 },
        { key: "name", title: "Location Name", width: 28 },
        { key: "realm", title: "Realm", width: 12 },
        { key: "type", title: "Type", width: 28 },
      ],
      rows: [
        {
          id: "L001",
          name: "Earth Cathedral",
          realm: "Surface",
          type: "landmark",
        },
        { id: "L002", name: "Vault 13", realm: "Underground", type: "vault" },
        { id: "L003", name: "Lost Hills", realm: "Surface", type: "base" },
        {
          id: "L004",
          name: "Necropolis",
          realm: "Underground",
          type: "dungeon",
        },
      ],
      page: 1,
      perPage: 20,
    },
  };
  return renderGrid(input).rawText;
};

// Example 3: Schedule/Agenda Mode
const scheduleExample = (): string => {
  const input: GridRendererInput = {
    mode: "schedule",
    spec: {
      width: 80,
      height: 30,
      title: "Upcoming Events",
      theme: "mono",
    },
    data: {
      events: [
        { time: "10:00", item: "Sprint Planning", location: "Room A" },
        { time: "11:30", item: "Design Review", location: "L305-DA11" },
        { time: "13:00", item: "Lunch Sync", location: "L305-DB22" },
        { time: "14:00", item: "Code Review", location: "Remote" },
        { time: "15:30", item: "Retro", location: "L305-DC33" },
      ],
      filters: {
        team: "dev",
        priority: "high",
      },
    },
  };
  return renderGrid(input).rawText;
};

// Example 4: Map Mode with LocId Overlays
const mapExample = (): string => {
  const overlays: LocIdOverlay[] = [
    { locId: "EARTH:SUR:L305-DA11", icon: "T", label: "Tasks: 3" },
    { locId: "EARTH:SUR:L305-DA12", icon: "N", label: "Notes: 1" },
    { locId: "EARTH:SUR:L305-DA21", icon: "E", label: "Events: 2" },
    { locId: "EARTH:SUR:L305-DB11", icon: "!", label: "Alert" },
    { locId: "EARTH:SUR:L305-DB22", icon: "T", label: "Tasks: 1" },
    { locId: "EARTH:SUR:L305-DB23", icon: "N", label: "Notes: 5" },
  ];

  const input: GridRendererInput = {
    mode: "map",
    spec: {
      width: 80,
      height: 30,
      title: "Spatial Map",
      theme: "mono",
    },
    data: {
      focusLocId: "EARTH:SUR:L305-DA11",
      overlays,
    },
  };
  return renderGrid(input).rawText;
};

// Example 5: Dashboard Mode
const dashboardExample = (): string => {
  const input: GridRendererInput = {
    mode: "dashboard",
    spec: {
      width: 80,
      height: 30,
      title: "System Dashboard",
      theme: "mono",
      ts: new Date().toISOString(),
    },
    data: {
      missions: [
        { status: "✓", title: "Phase 2 Audio Production Complete" },
        { status: "▶", title: "UGRID Core Implementation" },
        { status: "○", title: "API Route Integration" },
      ],
      stats: {
        "API Quota": "230/250 calls",
        "ollama Models": "5 loaded",
        "Active Sessions": "2",
        "Node Status": "✓ Online",
      },
      apiQuota: { used: 230, limit: 250 },
      nodeState: { status: "online", uptime: "12h 34m" },
      logs: [
        { time: "14:32", level: "INFO", message: "Render complete" },
        { time: "14:31", level: "DEBUG", message: "Layout generation" },
        { time: "14:30", level: "INFO", message: "Map overlays loaded" },
      ],
    },
  };
  return renderGrid(input).rawText;
};

// Test runner
export function runAllExamples() {
  console.log("=== UGRID CORE EXAMPLES ===\n");

  console.log("--- CALENDAR MODE ---");
  console.log(calendarExample());
  console.log("\n--- TABLE MODE ---");
  console.log(tableExample());
  console.log("\n--- SCHEDULE MODE ---");
  console.log(scheduleExample());
  console.log("\n--- MAP MODE ---");
  console.log(mapExample());
  console.log("\n--- DASHBOARD MODE ---");
  console.log(dashboardExample());
}

// Standalone test: Canvas primitives
export function testCanvasPrimitives() {
  console.log("=== CANVAS PRIMITIVES TEST ===\n");

  const c = new Canvas80x30();
  c.clear(" ");

  // Test box
  c.box(0, 0, 40, 15, "single", "Boxes");
  c.box(2, 2, 15, 12, "none");

  // Test text
  c.text(5, 3, 10, 5, "Wrapped\nText\nTest", { wrap: true });

  // Test table
  const cols = [
    { key: "id", title: "ID", width: 5 },
    { key: "val", title: "Value", width: 8 },
  ];
  const rows = [
    { id: "1", val: "100" },
    { id: "2", val: "200" },
  ];
  c.table(41, 0, 39, 15, cols, rows, { header: true, rowSep: true });

  // Output
  const lines = c.toLines();
  console.log(lines.join("\n"));
  console.log(`\nCanvas dimensions: ${c.width}x${c.height}`);
  console.log(`Lines rendered: ${lines.length}`);
}

if (typeof require !== "undefined" && require.main === module) {
  testCanvasPrimitives();
  console.log("\n");
  runAllExamples();
}
