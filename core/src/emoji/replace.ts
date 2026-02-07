import { isEmojiShortcode } from "./index";

export type EmojiRenderer = (shortcode: string) => string;

export function replaceEmojiShortcodes(
  text: string,
  render: EmojiRenderer
): string {
  return text.replace(/:[a-z0-9_+\-]+:/gi, (match) =>
    isEmojiShortcode(match) ? render(match) : match
  );
}
