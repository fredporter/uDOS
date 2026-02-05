import { Canvas80x30 } from "../canvas.js";
import { packageGrid } from "../pack.js";
import { GridCanvasSpec, TableColumn } from "../types.js";

export function renderTable(spec: GridCanvasSpec, input: any) {
  const c = new Canvas80x30();
  c.clear(" ");

  // Header
  c.box(0, 0, 80, 30, "single", spec.title);

  // Query info if provided
  if (input.query) {
    c.write(2, 1, `Query: ${input.query.slice(0, 70)}`);
  }

  // Row count
  const rowCount = input.rows?.length ?? 0;
  c.write(2, 2, `Rows: ${rowCount}`);

  // Table area
  const columns: TableColumn[] = input.columns || [
    { key: "id", title: "ID", width: 10 },
    { key: "name", title: "Name", width: 30 },
    { key: "value", title: "Value", width: 38 },
  ];

  c.table(1, 4, 78, 24, columns, input.rows || [], {
    header: true,
    rowSep: true,
  });

  // Footer: pagination
  const page = input.page ?? 1;
  const perPage = input.perPage ?? 20;
  const totalPages = Math.ceil(rowCount / perPage);
  c.write(
    2,
    29,
    `Page ${page}/${totalPages} | Offset: ${(page - 1) * perPage}`,
  );

  const lines = c.toLines();
  return packageGrid({ ...spec, mode: "table" }, lines);
}
