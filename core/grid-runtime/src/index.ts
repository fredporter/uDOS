/**
 * Main Grid Runtime Module
 * 
 * Exports all grid runtime types, utilities, and rendering pipeline
 */

export * from "./geometry";
export * from "./address";
export * from "./renderer";
export * from "./viewport";

// Phase 3: Code Block Parser exports
export * from "./expression-evaluator";
export * from "./code-block-parser";
export * from "./markdown-extractor";

// Phase 4: Location + Sparse World
export * from "./location-manager";
export * from "./sparse-world";
export * from "./pathfinding";

/**
 * Minimal Runtime stub for story execution.
 * 
 * This provides markdown parsing with story block extraction
 * for interactive form stories (.md with --- frontmatter and ```story blocks).
 */
export class Runtime {
  private markdown: string = "";
  private doc: any = null;
  private allowScripts: boolean = false;

  constructor(options?: { allowScripts?: boolean }) {
    this.allowScripts = options?.allowScripts ?? false;
  }

  load(markdown: string): void {
    this.markdown = markdown;
    this.doc = this.parseMarkdown(markdown);
  }

  getDocument(): any {
    return this.doc;
  }

  async execute(sectionId: string): Promise<any> {
    if (!this.doc || !this.doc.sections) {
      return { error: "No document loaded" };
    }

    // If no sectionId or it's null/undefined, return all sections
    if (!sectionId || sectionId === "null" || sectionId === "") {
      return {
        allSections: true,
        sections: this.doc.sections,
        frontmatter: this.doc.frontmatter,
      };
    }

    const section = this.doc.sections.find((s: any) => s.id === sectionId);
    if (!section) {
      return { error: `Section not found: ${sectionId}` };
    }

    // Return section data with fields (for form rendering)
    return {
      sectionId,
      title: section.title,
      fields: section.fields || [],
      text: section.text || "",
    };
  }

  private parseMarkdown(markdown: string): any {
    const lines = markdown.split("\n");
    const sections: any[] = [];

    // Parse frontmatter
    let frontmatter: any = {};
    let i = 0;
    if (lines[0] === "---") {
      i = 1;
      while (i < lines.length && lines[i] !== "---") {
        const line = lines[i];
        const colonIdx = line.indexOf(":");
        if (colonIdx > 0) {
          const key = line.substring(0, colonIdx).trim();
          const value = line.substring(colonIdx + 1).trim();
          // Remove quotes if present
          frontmatter[key] = value.replace(/^["']|["']$/g, "");
        }
        i++;
      }
      i++; // skip closing ---
    }

    // Parse sections (## headers) with story blocks
    let currentSection: any = null;
    let inCodeBlock = false;
    let codeBlockType = "";
    let codeBlockContent = "";

    while (i < lines.length) {
      const line = lines[i];
      
      if (line.startsWith("## ")) {
        // Save previous section
        if (currentSection) {
          sections.push(currentSection);
        }
        const title = line.substring(3).trim();
        currentSection = {
          id: title.toLowerCase().replace(/\s+/g, "-"),
          title,
          text: "",
          fields: [],
          blocks: [],
        };
      } else if (line.startsWith("```")) {
        const blockType = line.substring(3).trim();
        if (blockType === "story") {
          inCodeBlock = true;
          codeBlockType = "story";
          codeBlockContent = "";
        } else if (inCodeBlock && blockType === "") {
          // End of code block
          inCodeBlock = false;
          if (codeBlockType === "story" && currentSection) {
            const field = this.parseStoryBlock(codeBlockContent);
            if (field) {
              currentSection.fields.push(field);
            }
          }
          codeBlockType = "";
          codeBlockContent = "";
        }
      } else if (inCodeBlock) {
        codeBlockContent += line + "\n";
      } else if (currentSection && line.trim()) {
        // Regular text in section
        currentSection.text += line + "\n";
      }

      i++;
    }

    // Save last section
    if (currentSection) {
      sections.push(currentSection);
    }

    return {
      frontmatter,
      sections,
    };
  }

  private parseStoryBlock(content: string): any {
    const field: any = {};
    const lines = content.trim().split("\n");

    for (const line of lines) {
      const colonIdx = line.indexOf(":");
      if (colonIdx > 0) {
        const key = line.substring(0, colonIdx).trim();
        let value = line.substring(colonIdx + 1).trim();
        
        // Remove quotes
        value = value.replace(/^["']|["']$/g, "");
        
        // Parse special types
        if (key === "required") {
          field[key] = value.toLowerCase() === "true";
        } else if (key === "options") {
          // Options are parsed as a list in YAML format
          field[key] = [];
        } else {
          field[key] = value;
        }
      } else if (line.trim().startsWith("-") && field.options) {
        // Parse option items
        const optionValue = line.trim().substring(1).trim();
        field.options.push(optionValue);
      }
    }

    return Object.keys(field).length > 0 ? field : null;
  }
}

// Type definitions for tiles and entities
export interface Tile {
  id: string;
  type: "object" | "sprite" | "marker";
  static: boolean;
  palette?: number[]; // 5-bit indices
}

export interface ObjectTile extends Tile {
  type: "object";
  solid?: boolean;
  state?: string;
  udn?: {
    depthMm: number; // 0..3000 for buried objects
  };
}

export interface SpriteTile extends Tile {
  type: "sprite";
  frames: number;
  currentFrame?: number;
  animationSpeed?: number;
  facing?: "N" | "E" | "S" | "W" | "NE" | "NW" | "SE" | "SW";
}

export interface MarkerTile extends Tile {
  type: "marker";
  visible?: boolean;
  name: string;
  tags?: string[];
}

// Viewport and rendering types
export interface Viewport {
  cols: number;
  rows: number;
  name?: "standard" | "mini";
}

export interface RenderOptions {
  mode: "sextant" | "quadrant" | "shade" | "ascii";
  showTerrain: boolean;
  showSprites: boolean;
  showMarkers: boolean;
}

// Code block types for markdown integration
export interface TeletextBlock {
  type: "teletext";
  content: string; // raw sextant/ASCII grid
  variables?: Record<string, any>;
}

export interface GridBlock {
  type: "grid";
  definition: any; // YAML/JSON grid spec
  variables?: Record<string, any>;
}

export interface TilesBlock {
  type: "tiles";
  tiles: Tile[];
  manifest?: Record<string, any>;
}
