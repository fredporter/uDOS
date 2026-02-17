import { GridCanvasSpec, RenderResult } from "./types.js";
import { renderCalendarDay } from "./layouts/calendar.js";
import { renderTable } from "./layouts/table.js";
import { renderSchedule } from "./layouts/schedule.js";
import { renderMap } from "./layouts/map.js";
import { renderDashboard } from "./layouts/dashboard.js";
import { renderWorkflow } from "./layouts/workflow.js";

export interface GridRendererInput {
  mode: "calendar" | "table" | "schedule" | "map" | "dashboard" | "workflow";
  spec: GridCanvasSpec;
  data: any;
}

export function renderGrid(input: GridRendererInput): RenderResult {
  const { mode, spec, data } = input;

  switch (mode) {
    case "calendar":
      return renderCalendarDay(spec, data);
    case "table":
      return renderTable(spec, data);
    case "schedule":
      return renderSchedule(spec, data);
    case "map":
      return renderMap(spec, data);
    case "dashboard":
      return renderDashboard(spec, data);
    case "workflow":
      return renderWorkflow(spec, data);
    default:
      throw new Error(`Unknown render mode: ${mode}`);
  }
}

export {
  renderCalendarDay,
  renderTable,
  renderSchedule,
  renderMap,
  renderDashboard,
  renderWorkflow,
};

export * from "./canvas.js";
export * from "./types.js";
export * from "./pack.js";
