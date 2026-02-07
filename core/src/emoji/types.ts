export type EmojiShortcode = `:${string}:`;

export interface EmojiSourceMeta {
  name: string;
  raw: string;
}

export interface EmojiReference {
  source: EmojiSourceMeta;
  generatedAt: string; // YYYY-MM-DD
  shortcodes: EmojiShortcode[];
}
