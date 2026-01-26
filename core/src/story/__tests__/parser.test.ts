/**
 * Story Parser Tests
 *
 * Tests for parsing -story.md files into structured StoryState objects
 */

import { parseStoryFile, parseStoryBlock, extractStoryBlocks } from "../parser";
import type { StoryState, FormField } from "../types";

// Mock marked module since it uses ESM which Jest doesn't handle well
jest.mock("marked", () => ({
  marked: jest.fn((content: string) => Promise.resolve(`<p>${content}</p>`)),
}));

describe("Story Parser", () => {
  describe("parseStoryFile", () => {
    it("should parse minimal story file", () => {
      const content = `---
title: Test Story
type: story
---

# Section 1

Welcome to the story.
`;

      const result = parseStoryFile(content);

      expect(result.frontmatter.title).toBe("Test Story");
      expect(result.frontmatter.type).toBe("story");
      expect(result.sections).toHaveLength(1);
      expect(result.sections[0].title).toBe("Section 1");
      expect(result.currentSectionIndex).toBe(0);
      expect(result.isComplete).toBe(false);
    });

    it("should parse story with multiple sections", () => {
      const content = `---
title: Multi-Section Story
type: story
---

# Section 1

First section content.

---

# Section 2

Second section content.

`;

      const result = parseStoryFile(content);

      expect(result.sections).toHaveLength(2);
      expect(result.sections[0].title).toBe("Section 1");
      expect(result.sections[1].title).toBe("Section 2");
    });

    it("should extract story blocks from sections", () => {
      const content = `---
title: Story with Form
type: story
---

# User Info

Please tell us about yourself.

\`\`\`story
name: username
label: "What is your name?"
type: text
required: true
\`\`\`
`;

      const result = parseStoryFile(content);

      expect(result.sections[0].questions).toHaveLength(1);
      expect(result.sections[0].questions[0].name).toBe("username");
      expect(result.sections[0].questions[0].type).toBe("text");
      expect(result.sections[0].questions[0].required).toBe(true);
    });

    it("should throw error if no frontmatter", () => {
      const content = `# Section 1

No frontmatter here.
`;

      expect(() => parseStoryFile(content)).toThrow(
        "Story file must start with YAML frontmatter",
      );
    });
  });

  describe("parseStoryBlock", () => {
    it("should parse text field", () => {
      const block = `name: username
label: "Enter your username"
type: text
required: true
placeholder: "username"`;

      const field = parseStoryBlock(block);

      expect(field).not.toBeNull();
      expect(field!.name).toBe("username");
      expect(field!.label).toBe("Enter your username");
      expect(field!.type).toBe("text");
      expect(field!.required).toBe(true);
      expect(field!.placeholder).toBe("username");
    });

    it("should parse select field with options", () => {
      const block = `name: role
label: "Select your role"
type: select
required: true
options:
  - "User"
  - "Admin"
  - "Developer"`;

      const field = parseStoryBlock(block);

      expect(field).not.toBeNull();
      expect(field!.type).toBe("select");
      expect(field!.options).toEqual(["User", "Admin", "Developer"]);
    });

    it("should return null for block missing required fields", () => {
      const block = `type: text
placeholder: "Missing name and label"`;

      const field = parseStoryBlock(block);

      expect(field).toBeNull();
    });
  });

  describe("extractStoryBlocks", () => {
    it("should extract multiple story blocks from markdown", () => {
      const markdown = `# Section Title

Some content here.

\`\`\`story
name: field1
label: "Field 1"
type: text
\`\`\`

More content.

\`\`\`story
name: field2
label: "Field 2"
type: email
\`\`\`
`;

      const blocks = extractStoryBlocks(markdown);

      expect(blocks).toHaveLength(2);
      expect(blocks[0].name).toBe("field1");
      expect(blocks[1].name).toBe("field2");
    });

    it("should handle markdown with no story blocks", () => {
      const markdown = `# Section Title

Just regular markdown content.
`;

      const blocks = extractStoryBlocks(markdown);

      expect(blocks).toHaveLength(0);
    });
  });
});
