/**
 * Minimal runtime orchestrator for markdown scripts.
 */

import { MarkdownParser } from "../parser/markdown";
import { ExecutorFactory } from "../executors/factory";
import {
  Document,
  ExecutionContext,
  ExecutorResult,
  RuntimeBlock,
  RuntimeConfig,
  StateValue,
} from "../types";

export class Runtime {
  private document: Document | null = null;
  private state: StateValue = {};
  private config: RuntimeConfig;
  private history: string[] = [];
  private variables: Map<string, any> = new Map();

  constructor(config: RuntimeConfig = {}) {
    this.config = config;
  }

  load(markdown: string): void {
    this.document = MarkdownParser.parse(markdown);
    if (this.document.frontmatter.stateDefaults === "reset") {
      this.state = {};
    }
  }

  getDocument(): Document | null {
    return this.document;
  }

  getState(): StateValue {
    return JSON.parse(JSON.stringify(this.state));
  }

  setState(state: StateValue): void {
    this.state = JSON.parse(JSON.stringify(state));
  }

  async execute(sectionId: string): Promise<ExecutorResult> {
    if (!this.document) {
      return { success: false, error: "No document loaded" };
    }

    const section = this.document.sections.find((s) => s.id === sectionId);
    if (!section) {
      return { success: false, error: `Section not found: ${sectionId}` };
    }

    const context: ExecutionContext = {
      state: this.state,
      section,
      history: this.history,
      variables: this.variables,
    };

    let aggregatedOutput = "";
    let lastResult: ExecutorResult = { success: true };

    for (const block of section.blocks) {
      context.currentBlock = block as RuntimeBlock;
      const result = await ExecutorFactory.execute(block, context);
      lastResult = result;

      if (!result.success) {
        return result;
      }

      if (result.stateChanges) {
        this.state = { ...this.state, ...result.stateChanges };
        context.state = this.state;
      }

      if (result.output) {
        aggregatedOutput += result.output + "\n";
      }

      if (result.nextSection) {
        return { ...result, output: aggregatedOutput.trim() || result.output };
      }
    }

    return {
      ...lastResult,
      success: true,
      output: aggregatedOutput.trim() || lastResult.output,
    };
  }
}
