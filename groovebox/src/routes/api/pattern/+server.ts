/**
 * Groovebox Pattern API
 *
 * Save and load drum patterns
 * TODO: Implement actual file system storage
 */

import { json } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

// In-memory storage for now
let patterns: Record<string, any> = {};

export const POST: RequestHandler = async ({ request }) => {
  try {
    const pattern = await request.json();
    const id = pattern.name || `pattern_${Date.now()}`;
    patterns[id] = pattern;

    console.log("[Groovebox API] Saved pattern:", id);

    return json({ success: true, id });
  } catch (error) {
    console.error("[Groovebox API] Save failed:", error);
    return json({ success: false, error: String(error) }, { status: 500 });
  }
};

export const GET: RequestHandler = async ({ url }) => {
  const id = url.searchParams.get("id");

  if (id && patterns[id]) {
    return json(patterns[id]);
  }

  // Return list of all patterns
  return json(
    Object.keys(patterns).map((key) => ({
      id: key,
      name: patterns[key].name,
    }))
  );
};
