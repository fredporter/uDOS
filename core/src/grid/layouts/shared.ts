import { GridLocationRef, ScheduleItem, TaskItem, WorkflowStep } from "../types.js";

export function spatialRef(value: GridLocationRef | undefined): string | null {
  const ref = value?.placeRef || value?.locId || value?.location;
  if (!ref || typeof ref !== "string") return null;
  const trimmed = ref.trim();
  return trimmed || null;
}

export function compactSpatialRef(ref: string): string {
  const parts = ref.split(":");
  if (parts.length >= 3) return parts.slice(-2).join(":");
  return ref;
}

export function normalizeTaskRows(tasks: TaskItem[] = []): TaskItem[] {
  return [...tasks].sort((a, b) => {
    const dueCmp = (a.due || "").localeCompare(b.due || "");
    if (dueCmp !== 0) return dueCmp;
    const textCmp = (a.text || "").localeCompare(b.text || "");
    if (textCmp !== 0) return textCmp;
    return (a.id || "").localeCompare(b.id || "");
  });
}

export type ScheduleRow = {
  time: string;
  item: string;
  location: string;
  channel?: string;
  _ref?: string;
};

export function normalizeScheduleRows(items: ScheduleItem[] = []): ScheduleRow[] {
  return [...items]
    .map((entry) => {
      const ref = spatialRef(entry) || "";
      return {
        time: entry.start || entry.time || "",
        item: entry.item || entry.title || "",
        location: ref || entry.location || "",
        channel: entry.channel || "",
        _ref: ref || undefined,
      };
    })
    .sort((a, b) => {
      const t = (a.time || "").localeCompare(b.time || "");
      if (t !== 0) return t;
      const i = (a.item || "").localeCompare(b.item || "");
      if (i !== 0) return i;
      return (a.location || "").localeCompare(b.location || "");
    });
}

const stateOrder: Record<WorkflowStep["state"], number> = {
  in_progress: 0,
  blocked: 1,
  todo: 2,
  done: 3,
};

export function normalizeWorkflowRows(steps: WorkflowStep[] = []): WorkflowStep[] {
  return [...steps].sort((a, b) => {
    const stateCmp = stateOrder[a.state] - stateOrder[b.state];
    if (stateCmp !== 0) return stateCmp;
    const titleCmp = (a.title || "").localeCompare(b.title || "");
    if (titleCmp !== 0) return titleCmp;
    return (a.id || "").localeCompare(b.id || "");
  });
}

export function workflowStateGlyph(state: WorkflowStep["state"]): string {
  switch (state) {
    case "done":
      return "[x]";
    case "in_progress":
      return "[>]";
    case "blocked":
      return "[!]";
    default:
      return "[ ]";
  }
}
