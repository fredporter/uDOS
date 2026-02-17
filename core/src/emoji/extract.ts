import { isEmojiShortcode } from "./index.js";
import type { EmojiShortcode } from "./types.js";

const EMOJI_REGEX = /:[a-z0-9_+\-]+:/gi;

export function extractEmojiShortcodes(text: string): EmojiShortcode[] {
  const matches = text.match(EMOJI_REGEX) ?? [];
  const shortcodes: EmojiShortcode[] = [];
  for (const match of matches) {
    if (isEmojiShortcode(match)) {
      shortcodes.push(match);
    }
  }
  return shortcodes;
}
