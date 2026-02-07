import { isEmojiShortcode } from "./index";
import type { EmojiShortcode } from "./types";

const EMOJI_REGEX = /:[a-z0-9_+\-]+:/gi;

export function extractEmojiShortcodes(text: string): EmojiShortcode[] {
  const matches = text.match(EMOJI_REGEX) ?? [];
  return matches.filter(isEmojiShortcode);
}
