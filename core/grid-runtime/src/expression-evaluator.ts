/**
 * ExpressionEvaluator - Variable expression parsing and interpolation
 * Phase 3: Code Block Parser component
 *
 * Capabilities:
 * - Parse variable references: $var, $obj.prop, $arr[0]
 * - Nested access: $a.b.c, $a[0].b, etc.
 * - Text interpolation: "At #{$pos}" → "At AA10"
 * - Expression evaluation from runtime state
 */

/**
 * Runtime state container for variable evaluation
 * Values can be primitives, objects, or arrays
 */
export interface RuntimeState {
  [key: string]: any;
}

/**
 * Parsed expression result
 */
export interface ExpressionResult {
  type: "variable" | "literal" | "interpolated";
  value: any;
  source: string; // Original source text
}

/**
 * ExpressionEvaluator: Safely evaluate variable expressions and interpolate text
 */
export class ExpressionEvaluator {
  private state: RuntimeState;

  /**
   * Constructor with initial state
   * @param initialState - Runtime variables (e.g., { player: { pos: { tile: "AA10" } } })
   */
  constructor(initialState: RuntimeState = {}) {
    this.state = { ...initialState };
  }

  /**
   * Set or update state variable
   * @param key - Variable name
   * @param value - Variable value
   */
  public setState(key: string, value: any): void {
    this.state[key] = value;
  }

  /**
   * Get entire state (for debugging)
   */
  public getState(): RuntimeState {
    return { ...this.state };
  }

  /**
   * Evaluate a variable expression
   * Supports: $var, $obj.prop, $arr[0], $a.b.c, $a[0].b[1].c
   * @param expression - Expression to evaluate (e.g., "$player.pos.tile")
   * @returns ExpressionResult with parsed value
   */
  public evaluateVariable(expression: string): ExpressionResult {
    const source = expression;

    // Remove leading $
    if (!expression.startsWith("$")) {
      return {
        type: "literal",
        value: expression,
        source,
      };
    }

    const path = expression.slice(1); // Remove $

    try {
      const value = this.resolvePath(path);
      return {
        type: "variable",
        value,
        source,
      };
    } catch (error) {
      // Variable not found - return undefined
      return {
        type: "variable",
        value: undefined,
        source,
      };
    }
  }

  /**
   * Interpolate text with variable substitution
   * Supports: "At #{$player.pos.tile}" → "At AA10"
   * @param text - Text with #{...} placeholders
   * @returns Interpolated text
   */
  public interpolate(text: string): string {
    // Match #{...} patterns
    const regex = /#{([^}]+)}/g;

    return text.replace(regex, (match, expr) => {
      const result = this.evaluateVariable(expr.trim());

      // Convert value to string, handle undefined/null
      if (result.value === undefined || result.value === null) {
        return ""; // Empty string for undefined
      }

      if (typeof result.value === "object") {
        return JSON.stringify(result.value);
      }

      return String(result.value);
    });
  }

  /**
   * Parse a path and resolve it in state
   * Internal method for recursive path resolution
   * @param path - Dot-notation path (e.g., "player.pos.tile" or "inventory[0].name")
   * @returns Resolved value
   */
  private resolvePath(path: string): any {
    // Split path by . and [ ]
    // Examples:
    // "player" → ["player"]
    // "player.pos.tile" → ["player", "pos", "tile"]
    // "inventory[0]" → ["inventory", "[0]"]
    // "inventory[0].name" → ["inventory", "[0]", "name"]

    const segments = this.parsePathSegments(path);
    let current = this.state;

    for (const segment of segments) {
      if (current === null || current === undefined) {
        throw new Error(`Cannot access property of undefined at path: ${path}`);
      }

      // Check if segment is array index [n]
      const arrayMatch = segment.match(/^\[(\d+)\]$/);
      if (arrayMatch) {
        const index = parseInt(arrayMatch[1], 10);
        if (!Array.isArray(current)) {
          throw new Error(`Expected array but got ${typeof current} at path: ${path}`);
        }
        current = current[index];
      } else {
        // Regular property access
        current = current[segment];
      }
    }

    return current;
  }

  /**
   * Parse path into segments for resolution
   * Examples:
   * "a.b.c" → ["a", "b", "c"]
   * "a[0].b" → ["a", "[0]", "b"]
   * "arr[0][1]" → ["arr", "[0]", "[1]"]
   * @param path - Path string
   * @returns Array of segments
   */
  private parsePathSegments(path: string): string[] {
    const segments: string[] = [];
    let current = "";
    let i = 0;

    while (i < path.length) {
      const char = path[i];

      if (char === ".") {
        // Dot separator
        if (current) {
          segments.push(current);
          current = "";
        }
        i++;
      } else if (char === "[") {
        // Array index start
        if (current) {
          segments.push(current);
          current = "";
        }

        // Collect until ]
        let bracket = "[";
        i++;
        while (i < path.length && path[i] !== "]") {
          bracket += path[i];
          i++;
        }
        if (i < path.length) {
          bracket += "]"; // Add closing ]
          i++;
        }

        segments.push(bracket);
      } else {
        // Regular character
        current += char;
        i++;
      }
    }

    // Add remaining segment
    if (current) {
      segments.push(current);
    }

    return segments;
  }

  /**
   * Evaluate multiple expressions
   * @param expressions - Array of expressions
   * @returns Array of results
   */
  public evaluateMultiple(expressions: string[]): ExpressionResult[] {
    return expressions.map((expr) => this.evaluateVariable(expr));
  }

  /**
   * Interpolate multiple text strings
   * @param texts - Array of text strings
   * @returns Array of interpolated strings
   */
  public interpolateMultiple(texts: string[]): string[] {
    return texts.map((text) => this.interpolate(text));
  }
}
