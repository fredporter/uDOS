import { Canvas } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec, TableColumn } from "../types.js";

function clamp(v: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, v));
}

export function renderTable(spec: GridCanvasSpec, input: any) {
  const width = clamp(Math.floor(spec.width || 80), 40, 220);
  const height = clamp(Math.floor(spec.height || 30), 16, 120);

  const c = new Canvas(width, height);
  c.clear(" ");

  c.box(0, 0, width, height, "single", (spec.title || "Table").slice(0, Math.max(0, width - 4)));

  if (input.query) {
    c.write(2, 1, `Query: ${String(input.query).slice(0, Math.max(1, width - 10))}`);
  }

  const rowCount = input.rows?.length ?? 0;
  c.write(2, 2, `Rows: ${rowCount}`.slice(0, Math.max(1, width - 4)));

  const columns: TableColumn[] = input.columns || [
    { key: "id", title: "ID", width: Math.max(8, Math.floor((width - 6) * 0.15)) },
    { key: "name", title: "Name", width: Math.max(12, Math.floor((width - 6) * 0.35)) },
    { key: "value", title: "Value", width: Math.max(12, Math.floor((width - 6) * 0.45)) },
  ];

  const tableY = 4;
  const tableH = Math.max(6, height - 6);
  c.table(1, tableY, width - 2, tableH, columns, input.rows || [], {
    header: true,
    rowSep: true,
  });

  const page = input.page ?? 1;
  const perPage = input.perPage ?? 20;
  const totalPages = Math.max(1, Math.ceil(rowCount / perPage));
  c.write(2, height - 1, `Page ${page}/${totalPages} | Offset: ${(page - 1) * perPage}`.slice(0, Math.max(1, width - 4)));

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "table", width, height }, lines);
}
