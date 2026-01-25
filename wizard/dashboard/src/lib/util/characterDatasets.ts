/**
 * Character Datasets for Pixel Editor
 *
 * Defines various character sets including ASCII mappings, block graphics,
 * emojis, and teletext special characters
 */

export interface CharacterSet {
  name: string;
  description: string;
  codes: number[];
  type: "ascii" | "unicode" | "emoji" | "custom";
  asciiMapping?: Record<number, string>; // Maps character code to ASCII representation
  noMargin?: boolean; // If true, characters fill entire grid (for block graphics)
  githubShortcodes?: Record<number, string>; // Maps character code to GitHub :emoji: shortcode
  sizeHints?: Record<number, number>; // Scale factor per emoji (0.5-2.0, default 1.0)
  renderPadding?: number; // Minimum padding in pixels (default 1px)
  pairedSet?: string; // ID of corresponding mono/color set for toggling
}

/**
 * uDOS Block Graphics Set
 *
 * Mathematical Design:
 * - Base resolution: 8×8 pixels (64 pixels total)
 * - Display resolution: 24×24 pixels (3× scaling - perfect divisibility)
 * - Theoretical combinations: 2^64 = 18,446,744,073,709,551,616
 * - Practical set: ~80-96 useful geometric patterns
 *
 * Pattern Categories:
 * - Halves (4): top, bottom, left, right
 * - Thirds (6): horizontal and vertical divisions
 * - Quarters (4): TL, TR, BL, BR
 * - Diagonal quarters (2): TL+BR, TR+BL
 * - Three-quarters (4): all except one quarter
 * - Shading (5): 20%, 40%, 50%, 60%, 80%
 * - Checkerboard patterns (3): standard, inverse, diagonal
 * - Edge patterns (8): thick edges on each side
 * - Corner patterns (4): rounded corners
 * - Diagonal lines (4): /, \, thin and thick
 * - Dots/circles (3): centered, corner clusters
 * - Full/empty (2)
 *
 * Total practical patterns: ~80+ characters
 * 8×8 is classic computer graphics resolution (C64, Apple II, arcade sprites)
 * ASCII mapping shows text-only fallback representation
 */
export const TELETEXT_BLOCK_GRAPHICS: CharacterSet = {
  name: "uDOS Block Graphics",
  description:
    "8×8 base resolution block graphics (24×24 display @ 3× scaling)",
  type: "custom",
  noMargin: true, // Fill entire 24×24 grid
  codes: [
    // === FULL/EMPTY (2) ===
    0x2588, // █ Full block
    0x0020, // ' ' Space (empty)

    // === BASIC HALVES (4) ===
    0x2580, // ▀ Upper half block
    0x2584, // ▄ Lower half block
    0x258c, // ▌ Left half block
    0x2590, // ▐ Right half block

    // === THIRDS - HORIZONTAL (2) ===
    0x2581, // ▁ Lower 1/8 (use for lower third)
    0x2594, // ▔ Upper 1/8 (use for upper third)

    // === THIRDS - VERTICAL (2) ===
    0x258f, // ▏ Left 1/8 (use for left third)
    0x2595, // ▕ Right 1/8 (use for right third)

    // === QUARTERS (4) ===
    0x2598, // ▘ Quadrant upper left
    0x259d, // ▝ Quadrant upper right
    0x2596, // ▖ Quadrant lower left
    0x2597, // ▗ Quadrant lower right

    // === DIAGONAL QUARTERS (2) ===
    0x259a, // ▚ Quadrant upper left and lower right (diagonal /)
    0x259e, // ▞ Quadrant upper right and lower left (diagonal \)

    // === THREE-QUARTERS (4) ===
    0x259b, // ▛ Quadrant upper left and upper right and lower left
    0x259c, // ▜ Quadrant upper left and upper right and lower right
    0x259f, // ▟ Quadrant upper left and lower left and lower right
    0x2599, // ▙ Quadrant upper left and lower left and lower right (alternate)

    // === TWO ADJACENT QUARTERS (6) ===
    // Top half already covered: 0x2580
    // Bottom half already covered: 0x2584
    // Left half already covered: 0x258c
    // Right half already covered: 0x2590
    // Diagonals already covered: 0x259a, 0x259e

    // === FRACTIONAL BLOCKS - VERTICAL (7) ===
    0x2582, // ▂ Lower 1/4
    0x2583, // ▃ Lower 3/8
    0x2585, // ▅ Lower 5/8
    0x2586, // ▆ Lower 3/4
    0x2587, // ▇ Lower 7/8

    // === FRACTIONAL BLOCKS - HORIZONTAL (7) ===
    0x258a, // ▊ Left 3/4
    0x258b, // ▋ Left 5/8
    0x258d, // ▍ Left 3/8
    0x258e, // ▎ Left 1/4
    0x2589, // ▉ Left 7/8

    // === SHADING PATTERNS (5) ===
    0x2591, // ░ Light shade (25%)
    0x2592, // ▒ Medium shade (50%)
    0x2593, // ▓ Dark shade (75%)
    0x2596, // ▖ Additional pattern (can be reassigned)
    0x2597, // ▗ Additional pattern (can be reassigned)

    // === BOX DRAWING - SINGLE LINES (11) ===
    0x2500, // ─ Horizontal line
    0x2502, // │ Vertical line
    0x250c, // ┌ Down and right
    0x2510, // ┐ Down and left
    0x2514, // └ Up and right
    0x2518, // ┘ Up and left
    0x251c, // ├ Vertical and right
    0x2524, // ┤ Vertical and left
    0x252c, // ┬ Horizontal and down
    0x2534, // ┴ Horizontal and up
    0x253c, // ┼ Cross

    // === BOX DRAWING - DOUBLE LINES (11) ===
    0x2550, // ═ Double horizontal
    0x2551, // ║ Double vertical
    0x2554, // ╔ Double down and right
    0x2557, // ╗ Double down and left
    0x255a, // ╚ Double up and right
    0x255d, // ╝ Double up and left
    0x2560, // ╠ Double vertical and right
    0x2563, // ╣ Double vertical and left
    0x2566, // ╦ Double horizontal and down
    0x2569, // ╩ Double horizontal and up
    0x256c, // ╬ Double cross

    // === BOX DRAWING - ROUNDED CORNERS (4) ===
    0x256d, // ╭ Light arc down and right
    0x256e, // ╮ Light arc down and left
    0x256f, // ╯ Light arc up and left
    0x2570, // ╰ Light arc up and right

    // === DIAGONAL LINES (2) ===
    0x2571, // ╱ Diagonal /
    0x2572, // ╲ Diagonal \
    0x2573, // ╳ Diagonal cross X

    // === SPECIAL PATTERNS (8) ===
    0x25a0, // ■ Black square
    0x25a1, // □ White square
    0x25aa, // ▪ Black small square (centered)
    0x25ab, // ▫ White small square (centered)
    0x25ac, // ▬ Black rectangle
    0x25ad, // ▭ White rectangle
    0x25ae, // ▮ Black vertical rectangle
    0x25af, // ▯ White vertical rectangle
  ],
  asciiMapping: {
    // Full/empty
    0x2588: "#", // Full block
    0x0020: " ", // Space

    // Halves
    0x2580: "^", // Upper half
    0x2584: "_", // Lower half
    0x258c: "[", // Left half
    0x2590: "]", // Right half

    // Thirds
    0x2581: "_", // Lower third
    0x2594: "^", // Upper third
    0x258f: "|", // Left third
    0x2595: "|", // Right third

    // Quarters
    0x2598: "`", // Upper left
    0x259d: "'", // Upper right
    0x2596: ",", // Lower left
    0x2597: ".", // Lower right

    // Diagonal quarters
    0x259a: "/", // Diagonal /
    0x259e: "\\", // Diagonal \

    // Three-quarters
    0x259b: "F", // Three quarters (upper + lower left)
    0x259c: "T", // Three quarters (upper + lower right)
    0x259f: "L", // Three quarters (left + lower right)
    0x2599: "J", // Three quarters (left + upper right)

    // Fractional blocks - vertical
    0x2582: "_", // Lower 1/4
    0x2583: "_", // Lower 3/8
    0x2585: "#", // Lower 5/8
    0x2586: "#", // Lower 3/4
    0x2587: "#", // Lower 7/8

    // Fractional blocks - horizontal
    0x258a: "[", // Left 3/4
    0x258b: "[", // Left 5/8
    0x258d: "|", // Left 3/8
    0x258e: "|", // Left 1/4
    0x2589: "[", // Left 7/8

    // Shading
    0x2591: ".", // Light shade
    0x2592: ":", // Medium shade
    0x2593: "%", // Dark shade

    // Box drawing - single lines
    0x2500: "-", // Horizontal
    0x2502: "|", // Vertical
    0x250c: "+", // Corner TL
    0x2510: "+", // Corner TR
    0x2514: "+", // Corner BL
    0x2518: "+", // Corner BR
    0x251c: "+", // T-right
    0x2524: "+", // T-left
    0x252c: "+", // T-down
    0x2534: "+", // T-up
    0x253c: "+", // Cross

    // Box drawing - double lines
    0x2550: "=", // Double horizontal
    0x2551: "|", // Double vertical
    0x2554: "+", // Double corner TL
    0x2557: "+", // Double corner TR
    0x255a: "+", // Double corner BL
    0x255d: "+", // Double corner BR
    0x2560: "+", // Double T-right
    0x2563: "+", // Double T-left
    0x2566: "+", // Double T-down
    0x2569: "+", // Double T-up
    0x256c: "+", // Double cross

    // Box drawing - rounded corners
    0x256d: "+", // Arc TL
    0x256e: "+", // Arc TR
    0x256f: "+", // Arc BR
    0x2570: "+", // Arc BL

    // Diagonal lines
    0x2571: "/", // Diagonal /
    0x2572: "\\", // Diagonal \
    0x2573: "X", // Diagonal cross

    // Special patterns
    0x25a0: "#", // Black square
    0x25a1: "O", // White square
    0x25aa: "*", // Small black
    0x25ab: "o", // Small white
    0x25ac: "-", // Black rectangle
    0x25ad: "-", // White rectangle
    0x25ae: "|", // Black vertical rectangle
    0x25af: "|", // White vertical rectangle
  },
};

/**
 * Box Drawing Characters
 * Line-based graphics for tables and borders
 */
export const BOX_DRAWING: CharacterSet = {
  name: "Box Drawing",
  description: "Single and double line box drawing characters",
  type: "unicode",
  noMargin: true, // Fill entire grid for precise alignment
  codes: [
    // Single lines
    0x2500, // ─ Horizontal
    0x2502, // │ Vertical
    0x250c, // ┌ Down and right
    0x2510, // ┐ Down and left
    0x2514, // └ Up and right
    0x2518, // ┘ Up and left
    0x251c, // ├ Vertical and right
    0x2524, // ┤ Vertical and left
    0x252c, // ┬ Horizontal and down
    0x2534, // ┴ Horizontal and up
    0x253c, // ┼ Cross
    // Double lines
    0x2550, // ═ Horizontal double
    0x2551, // ║ Vertical double
    0x2554, // ╔ Down double and right
    0x2557, // ╗ Down double and left
    0x255a, // ╚ Up double and right
    0x255d, // ╝ Up double and left
    0x2560, // ╠ Vertical double and right
    0x2563, // ╣ Vertical double and left
    0x2566, // ╦ Horizontal double and down
    0x2569, // ╩ Horizontal double and up
    0x256c, // ╬ Cross double
  ],
  asciiMapping: {
    0x2500: "-",
    0x2502: "|",
    0x250c: "+",
    0x2510: "+",
    0x2514: "+",
    0x2518: "+",
    0x251c: "+",
    0x2524: "+",
    0x252c: "+",
    0x2534: "+",
    0x253c: "+",
    0x2550: "=",
    0x2551: "|",
    0x2554: "+",
    0x2557: "+",
    0x255a: "+",
    0x255d: "+",
    0x2560: "+",
    0x2563: "+",
    0x2566: "+",
    0x2569: "+",
    0x256c: "+",
  },
};

/**
 * ASCII Printable Characters
 * Standard ASCII 32-126
 */
export const ASCII_PRINTABLE: CharacterSet = {
  name: "ASCII Printable",
  description: "Standard ASCII characters (32-126)",
  type: "ascii",
  codes: Array.from({ length: 95 }, (_, i) => i + 32),
};

// ============================================================================
// EMOJI SETS - NOTO COLOR EMOJI (Full Color)
// Font: NotoColorEmoji.ttf
// ============================================================================

/**
 * Noto Color Emoji - Full Set
 * Comprehensive emoji collection rendered in full color
 * Use with: /fonts/NotoColorEmoji.ttf
 */
export const EMOJI_COLOR_FULL: CharacterSet = {
  name: "Color Emoji (Full)",
  description:
    "Complete color emoji set from Noto Color Emoji - GitHub :emoji: compatible",
  type: "emoji",
  renderPadding: 1, // 1px minimum border
  pairedSet: "emoji-mono", // Can toggle to mono version
  codes: [
    // === MATCHED CORE SET (available in both mono & color) ===
    // FACES - SMILING
    0x1f600,
    0x1f603,
    0x1f604,
    0x1f601,
    0x1f606,
    0x1f60a,
    0x1f609,
    // FACES - AFFECTION
    0x1f60d,
    0x1f61c,
    // FACES - NEUTRAL/NEGATIVE
    0x1f610,
    0x1f611,
    0x1f60f,
    0x1f612,
    0x1f614,
    0x1f622,
    0x1f621,
    0x1f620,
    // SPECIAL
    0x1f480,
    // GESTURES & HANDS
    0x1f44d,
    0x1f44e,
    0x1f44a,
    0x270a,
    0x1f44f,
    0x1f64f,
    0x1f44b,
    0x270b,
    0x1f44c,
    0x270c,
    0x1f448,
    0x1f449,
    0x1f446,
    0x1f447,
    0x261d,
    0x1f4aa,
    // HEARTS
    0x2764,
    0x1f494,
    0x1f495,
    0x1f496,
    0x1f497,
    0x1f498,
    0x2665,
    // STARS & SPARKLES
    0x2b50,
    0x1f31f,
    0x2728,
    0x1f4ab,
    // WEATHER
    0x2600,
    0x26c5,
    0x2601,
    0x2744,
    0x1f319,
    0x1f31d,
    0x1f31b,
    // SYMBOLS - BASIC
    0x2705,
    0x274c,
    0x2795,
    0x2796,
    0x2716,
    0x2797,
    0x2757,
    0x2753,
    0x26a0,
    0x1f6ab,
    0x1f525,
    0x1f4a5,
    0x2139,
    // ARROWS
    0x2b06,
    0x27a1,
    0x2b07,
    0x2b05,
    0x2194,
    0x2195,
    0x21a9,
    0x21aa,
    // MEDIA CONTROLS
    0x25b6,
    0x23f8,
    0x23f9,
    0x23fa,
    0x23ed,
    0x23ee,
    0x23e9,
    0x23ea,
    0x1f509,
    0x1f50a,
    0x1f507,
    // OBJECTS - TECH
    0x1f4a1,
    0x1f50d,
    0x1f511,
    0x1f512,
    0x1f513,
    0x1f4be,
    0x1f4bb,
    0x2328,
    0x1f4f1,
    0x1f4de,
    0x1f4e7,
    0x1f4c1,
    0x1f4c2,
    0x1f4dd,
    0x270f,
    0x1f4cc,
    // OBJECTS - TOOLS
    0x1f527,
    0x1f528,
    0x2699,
    0x1f50b,
    0x1f4a0,
    // MISC
    0x1f3ae,
    0x1f3b5,
    0x1f3b6,
    0x1f4f7,
    0x267b,
    0x269b,
    0x1f6a9,
    0x2693,
    0x1f3c6,
    0x1f451,

    // === COLOR-ONLY EXTENSIONS (richer emoji set) ===
    0x1f600, // 😀 Grinning face
    0x1f603, // 😃 Grinning face with big eyes
    0x1f604, // 😄 Grinning face with smiling eyes
    0x1f601, // 😁 Beaming face with smiling eyes
    0x1f606, // 😆 Grinning squinting face
    0x1f605, // 😅 Grinning face with sweat
    0x1f602, // 😂 Face with tears of joy
    0x1f923, // 🤣 Rolling on the floor laughing
    0x1f60a, // 😊 Smiling face with smiling eyes
    0x1f607, // 😇 Smiling face with halo
    0x1f642, // 🙂 Slightly smiling face
    0x1f643, // 🙃 Upside-down face
    0x1f609, // 😉 Winking face
    0x1f60c, // 😌 Relieved face
    0x1f972, // 🥲 Smiling face with tear

    // === FACES - AFFECTION ===
    0x1f60d, // 😍 Smiling face with heart-eyes
    0x1f970, // 🥰 Smiling face with hearts
    0x1f618, // 😘 Face blowing a kiss
    0x1f617, // 😗 Kissing face
    0x1f619, // 😙 Kissing face with smiling eyes
    0x1f61a, // 😚 Kissing face with closed eyes
    0x1f60b, // 😋 Face savoring food
    0x1f61c, // 😜 Winking face with tongue
    0x1f92a, // 🤪 Zany face
    0x1f61d, // 😝 Squinting face with tongue
    0x1f911, // 🤑 Money-mouth face

    // === FACES - NEUTRAL/SKEPTICAL ===
    0x1f914, // 🤔 Thinking face
    0x1f910, // 🤐 Zipper-mouth face
    0x1f928, // 🤨 Face with raised eyebrow
    0x1f610, // 😐 Neutral face
    0x1f611, // 😑 Expressionless face
    0x1f636, // 😶 Face without mouth
    0x1f60f, // 😏 Smirking face
    0x1f612, // 😒 Unamused face
    0x1f644, // 🙄 Face with rolling eyes
    0x1f62c, // 😬 Grimacing face
    0x1f925, // 🤥 Lying face

    // === FACES - SLEEPY ===
    0x1f60c, // 😌 Relieved face
    0x1f614, // 😔 Pensive face
    0x1f62a, // 😪 Sleepy face
    0x1f924, // 🤤 Drooling face
    0x1f634, // 😴 Sleeping face

    // === FACES - UNWELL ===
    0x1f637, // 😷 Face with medical mask
    0x1f912, // 🤒 Face with thermometer
    0x1f915, // 🤕 Face with head-bandage
    0x1f922, // 🤢 Nauseated face
    0x1f92e, // 🤮 Face vomiting
    0x1f927, // 🤧 Sneezing face
    0x1f975, // 🥵 Hot face
    0x1f976, // 🥶 Cold face
    0x1f974, // 🥴 Woozy face
    0x1f635, // 😵 Face with crossed-out eyes

    // === FACES - CONCERNED ===
    0x1f615, // 😕 Confused face
    0x1f61f, // 😟 Worried face
    0x1f641, // 🙁 Slightly frowning face
    0x2639, // ☹ Frowning face
    0x1f62e, // 😮 Face with open mouth
    0x1f62f, // 😯 Hushed face
    0x1f632, // 😲 Astonished face
    0x1f633, // 😳 Flushed face
    0x1f97a, // 🥺 Pleading face
    0x1f626, // 😦 Frowning face with open mouth
    0x1f627, // 😧 Anguished face
    0x1f628, // 😨 Fearful face
    0x1f630, // 😰 Anxious face with sweat
    0x1f625, // 😥 Sad but relieved face
    0x1f622, // 😢 Crying face
    0x1f62d, // 😭 Loudly crying face
    0x1f631, // 😱 Face screaming in fear
    0x1f616, // 😖 Confounded face
    0x1f623, // 😣 Persevering face
    0x1f61e, // 😞 Disappointed face
    0x1f613, // 😓 Downcast face with sweat

    // === FACES - NEGATIVE ===
    0x1f629, // 😩 Weary face
    0x1f62b, // 😫 Tired face
    0x1f971, // 🥱 Yawning face
    0x1f624, // 😤 Face with steam from nose
    0x1f621, // 😡 Pouting face
    0x1f620, // 😠 Angry face
    0x1f92c, // 🤬 Face with symbols on mouth
    0x1f608, // 😈 Smiling face with horns
    0x1f47f, // 👿 Angry face with horns
    0x1f480, // 💀 Skull
    0x1f4a9, // 💩 Pile of poo

    // === FACES - COSTUME ===
    0x1f921, // 🤡 Clown face
    0x1f479, // 👹 Ogre
    0x1f47a, // 👺 Goblin
    0x1f47b, // 👻 Ghost
    0x1f47d, // 👽 Alien
    0x1f47e, // 👾 Alien monster
    0x1f916, // 🤖 Robot

    // === FACES - CAT ===
    0x1f63a, // 😺 Grinning cat
    0x1f638, // 😸 Grinning cat with smiling eyes
    0x1f639, // 😹 Cat with tears of joy
    0x1f63b, // 😻 Smiling cat with heart-eyes
    0x1f63c, // 😼 Cat with wry smile
    0x1f63d, // 😽 Kissing cat
    0x1f640, // 🙀 Weary cat
    0x1f63f, // 😿 Crying cat
    0x1f63e, // 😾 Pouting cat

    // === GESTURES ===
    0x1f44d, // 👍 Thumbs up
    0x1f44e, // 👎 Thumbs down
    0x1f44a, // 👊 Oncoming fist
    0x270a, // ✊ Raised fist
    0x1f91b, // 🤛 Left-facing fist
    0x1f91c, // 🤜 Right-facing fist
    0x1f44f, // 👏 Clapping hands
    0x1f64c, // 🙌 Raising hands
    0x1f450, // 👐 Open hands
    0x1f64f, // 🙏 Folded hands
    0x1f91d, // 🤝 Handshake
    0x1f44b, // 👋 Waving hand
    0x1f590, // 🖐 Hand with fingers splayed
    0x270b, // ✋ Raised hand
    0x1f596, // 🖖 Vulcan salute
    0x1f44c, // 👌 OK hand
    0x270c, // ✌ Victory hand
    0x1f91e, // 🤞 Crossed fingers
    0x1f91f, // 🤟 Love-you gesture
    0x1f918, // 🤘 Sign of the horns
    0x1f448, // 👈 Backhand pointing left
    0x1f449, // 👉 Backhand pointing right
    0x1f446, // 👆 Backhand pointing up
    0x1f447, // 👇 Backhand pointing down
    0x261d, // ☝ Index pointing up
    0x1f4aa, // 💪 Flexed biceps

    // === HEARTS & SYMBOLS ===
    0x2764, // ❤ Red heart
    0x1f9e1, // 🧡 Orange heart
    0x1f49b, // 💛 Yellow heart
    0x1f49a, // 💚 Green heart
    0x1f499, // 💙 Blue heart
    0x1f49c, // 💜 Purple heart
    0x1f5a4, // 🖤 Black heart
    0x1f90d, // 🤍 White heart
    0x1f90e, // 🤎 Brown heart
    0x1f494, // 💔 Broken heart
    0x1f495, // 💕 Two hearts
    0x1f496, // 💖 Sparkling heart
    0x1f497, // 💗 Growing heart
    0x1f498, // 💘 Heart with arrow
    0x1f49d, // 💝 Heart with ribbon
    0x1f49e, // 💞 Revolving hearts
    0x1f49f, // 💟 Heart decoration

    // === STARS & SPARKLES ===
    0x2b50, // ⭐ Star
    0x1f31f, // 🌟 Glowing star
    0x1f4ab, // 💫 Dizzy
    0x2728, // ✨ Sparkles
    0x1fa90, // 🪐 Saturn (ringed planet)

    // === WEATHER ===
    0x2600, // ☀ Sun
    0x1f324, // 🌤 Sun behind small cloud
    0x26c5, // ⛅ Sun behind cloud
    0x1f325, // 🌥 Sun behind large cloud
    0x2601, // ☁ Cloud
    0x1f326, // 🌦 Sun behind rain cloud
    0x1f327, // 🌧 Cloud with rain
    0x26c8, // ⛈ Cloud with lightning and rain
    0x1f329, // 🌩 Cloud with lightning
    0x1f328, // 🌨 Cloud with snow
    0x2744, // ❄ Snowflake
    0x1f32c, // 🌬 Wind face
    0x1f32b, // 🌫 Fog
    0x1f308, // 🌈 Rainbow

    // === ANIMALS ===
    0x1f436, // 🐶 Dog face
    0x1f431, // 🐱 Cat face
    0x1f42d, // 🐭 Mouse face
    0x1f439, // 🐹 Hamster
    0x1f430, // 🐰 Rabbit face
    0x1f98a, // 🦊 Fox
    0x1f43b, // 🐻 Bear
    0x1f43c, // 🐼 Panda
    0x1f428, // 🐨 Koala
    0x1f42f, // 🐯 Tiger face
    0x1f981, // 🦁 Lion
    0x1f42e, // 🐮 Cow face
    0x1f437, // 🐷 Pig face
    0x1f438, // 🐸 Frog
    0x1f435, // 🐵 Monkey face
    0x1f414, // 🐔 Chicken
    0x1f427, // 🐧 Penguin
    0x1f426, // 🐦 Bird
    0x1f986, // 🦆 Duck
    0x1f989, // 🦉 Owl
    0x1f40d, // 🐍 Snake
    0x1f422, // 🐢 Turtle
    0x1f41f, // 🐟 Fish
    0x1f42c, // 🐬 Dolphin
    0x1f433, // 🐳 Whale
    0x1f419, // 🐙 Octopus
    0x1f41d, // 🐝 Honeybee
    0x1f98b, // 🦋 Butterfly

    // === FOOD ===
    0x1f34e, // 🍎 Red apple
    0x1f34f, // 🍏 Green apple
    0x1f34a, // 🍊 Tangerine
    0x1f34b, // 🍋 Lemon
    0x1f34c, // 🍌 Banana
    0x1f349, // 🍉 Watermelon
    0x1f347, // 🍇 Grapes
    0x1f353, // 🍓 Strawberry
    0x1f352, // 🍒 Cherries
    0x1f351, // 🍑 Peach
    0x1f35e, // 🍞 Bread
    0x1f355, // 🍕 Pizza
    0x1f354, // 🍔 Hamburger
    0x1f35f, // 🍟 French fries
    0x1f32e, // 🌮 Taco
    0x1f32f, // 🌯 Burrito
    0x1f37f, // 🍿 Popcorn
    0x1f366, // 🍦 Soft ice cream
    0x1f370, // 🍰 Shortcake
    0x1f382, // 🎂 Birthday cake
    0x2615, // ☕ Hot beverage
    0x1f37a, // 🍺 Beer mug
    0x1f377, // 🍷 Wine glass
    0x1f379, // 🍹 Tropical drink

    // === OBJECTS ===
    0x1f4a1, // 💡 Light bulb
    0x1f50d, // 🔍 Magnifying glass left
    0x1f50e, // 🔎 Magnifying glass right
    0x1f511, // 🔑 Key
    0x1f512, // 🔒 Locked
    0x1f513, // 🔓 Unlocked
    0x1f4be, // 💾 Floppy disk
    0x1f4bf, // 💿 Optical disk
    0x1f4bb, // 💻 Laptop
    0x1f5a5, // 🖥 Desktop computer
    0x2328, // ⌨ Keyboard
    0x1f4f1, // 📱 Mobile phone
    0x1f4de, // 📞 Telephone receiver
    0x1f4e7, // 📧 E-mail
    0x1f4c1, // 📁 File folder
    0x1f4c2, // 📂 Open file folder
    0x1f4dd, // 📝 Memo
    0x270f, // ✏ Pencil
    0x1f58a, // 🖊 Pen
    0x1f4cc, // 📌 Pushpin
    0x1f4ce, // 📎 Paperclip
    0x1f527, // 🔧 Wrench
    0x1f528, // 🔨 Hammer
    0x1f529, // 🔩 Nut and bolt
    0x2699, // ⚙ Gear

    // === SYMBOLS ===
    0x2705, // ✅ Check mark button
    0x274c, // ❌ Cross mark
    0x274e, // ❎ Cross mark button
    0x2795, // ➕ Plus
    0x2796, // ➖ Minus
    0x2716, // ✖ Multiplication X
    0x2797, // ➗ Division
    0x27b0, // ➰ Curly loop
    0x27bf, // ➿ Double curly loop
    0x2757, // ❗ Exclamation mark
    0x2753, // ❓ Question mark
    0x2754, // ❔ White question mark
    0x2755, // ❕ White exclamation mark
    0x203c, // ‼ Double exclamation
    0x2049, // ⁉ Exclamation question
    0x26a0, // ⚠ Warning
    0x1f6ab, // 🚫 Prohibited
    0x1f4af, // 💯 Hundred points
    0x1f525, // 🔥 Fire
    0x1f4a5, // 💥 Collision
    0x1f4a2, // 💢 Anger symbol
    0x1f4a3, // 💣 Bomb
    0x1f4a4, // 💤 Zzz (sleeping)
    0x1f4a8, // 💨 Dashing away
    0x1f4ac, // 💬 Speech balloon
    0x1f4ad, // 💭 Thought balloon

    // === ARROWS ===
    0x2b06, // ⬆ Up arrow
    0x2197, // ↗ Up-right arrow
    0x27a1, // ➡ Right arrow
    0x2198, // ↘ Down-right arrow
    0x2b07, // ⬇ Down arrow
    0x2199, // ↙ Down-left arrow
    0x2b05, // ⬅ Left arrow
    0x2196, // ↖ Up-left arrow
    0x2194, // ↔ Left-right arrow
    0x2195, // ↕ Up-down arrow
    0x21a9, // ↩ Right arrow curving left
    0x21aa, // ↪ Left arrow curving right
    0x1f503, // 🔃 Clockwise arrows
    0x1f504, // 🔄 Counterclockwise arrows

    // === NUMBERS ===
    0x0030, // 0
    0x0031, // 1
    0x0032, // 2
    0x0033, // 3
    0x0034, // 4
    0x0035, // 5
    0x0036, // 6
    0x0037, // 7
    0x0038, // 8
    0x0039, // 9
    0x0023, // # Hash
    0x002a, // * Asterisk
  ],
};

// ============================================================================
// EMOJI SETS - EMOJI ICON FONT (Monochrome)
// Font: EmojiIconFont.ttf
// ============================================================================

/**
 * Emoji Icon Font - Full Set
 * Comprehensive emoji collection rendered as monochrome icons
 * Use with: /fonts/EmojiIconFont.ttf
 */
export const EMOJI_MONO_FULL: CharacterSet = {
  name: "Mono Emoji (Full)",
  description:
    "Complete monochrome emoji set from Emoji Icon Font - GitHub :emoji: compatible",
  type: "emoji",
  // Note: noMargin is intentionally NOT set for emoji - they need margins to prevent cutoff
  renderPadding: 1, // 1px minimum border
  pairedSet: "emoji-color", // Can toggle to color version
  codes: [
    // === MATCHED CORE SET (same as color version for 1:1 toggle) ===
    // FACES - SMILING
    0x1f600, 0x1f603, 0x1f604, 0x1f601, 0x1f606, 0x1f60a, 0x1f609,
    // FACES - AFFECTION
    0x1f60d, 0x1f61c,
    // FACES - NEUTRAL/NEGATIVE
    0x1f610, 0x1f611, 0x1f60f, 0x1f612, 0x1f614, 0x1f622, 0x1f621, 0x1f620,
    // SPECIAL
    0x1f480,
    // GESTURES & HANDS
    0x1f44d, 0x1f44e, 0x1f44a, 0x270a, 0x1f44f, 0x1f64f, 0x1f44b, 0x270b,
    0x1f44c, 0x270c, 0x1f448, 0x1f449, 0x1f446, 0x1f447, 0x261d, 0x1f4aa,
    // HEARTS
    0x2764, 0x1f494, 0x1f495, 0x1f496, 0x1f497, 0x1f498, 0x2665,
    // STARS & SPARKLES
    0x2b50, 0x1f31f, 0x2728, 0x1f4ab,
    // WEATHER
    0x2600, 0x26c5, 0x2601, 0x2744, 0x1f319, 0x1f31d, 0x1f31b,
    // SYMBOLS - BASIC
    0x2705, 0x274c, 0x2795, 0x2796, 0x2716, 0x2797, 0x2757, 0x2753, 0x26a0,
    0x1f6ab, 0x1f525, 0x1f4a5, 0x2139,
    // ARROWS
    0x2b06, 0x27a1, 0x2b07, 0x2b05, 0x2194, 0x2195, 0x21a9, 0x21aa,
    // MEDIA CONTROLS
    0x25b6, 0x23f8, 0x23f9, 0x23fa, 0x23ed, 0x23ee, 0x23e9, 0x23ea, 0x1f509,
    0x1f50a, 0x1f507,
    // OBJECTS - TECH
    0x1f4a1, 0x1f50d, 0x1f511, 0x1f512, 0x1f513, 0x1f4be, 0x1f4bb, 0x2328,
    0x1f4f1, 0x1f4de, 0x1f4e7, 0x1f4c1, 0x1f4c2, 0x1f4dd, 0x270f, 0x1f4cc,
    // OBJECTS - TOOLS
    0x1f527, 0x1f528, 0x2699, 0x1f50b, 0x1f4a0,
    // MISC
    0x1f3ae, 0x1f3b5, 0x1f3b6, 0x1f4f7, 0x267b, 0x269b, 0x1f6a9, 0x2693,
    0x1f3c6, 0x1f451,
  ],
};

// Keep legacy exports for backward compatibility
export const EMOJI_FACES = EMOJI_COLOR_FULL;
export const EMOJI_SYMBOLS = EMOJI_MONO_FULL;

/**
 * Map Symbols - Terrain markers and survival indicators
 *
 * Uses Unicode symbols that render well in Teletext50 font
 * Designed for use with the 32-color terrain palette
 */
export const MAP_SYMBOLS: CharacterSet = {
  name: "Map Symbols",
  description: "Terrain markers, waypoints, and survival indicators",
  type: "unicode",
  noMargin: true,
  codes: [
    // === TERRAIN MARKERS ===
    0x25b2, // ▲ Mountain/Peak (up triangle)
    0x25bc, // ▼ Valley/Depression (down triangle)
    0x25c6, // ◆ Diamond (resource/POI)
    0x25cf, // ● Filled circle (settlement/camp)
    0x25cb, // ○ Empty circle (waypoint)
    0x25a0, // ■ Filled square (building/structure)
    0x25a1, // □ Empty square (ruins/abandoned)

    // === DIRECTIONAL ===
    0x2190, // ← West
    0x2191, // ↑ North
    0x2192, // → East
    0x2193, // ↓ South
    0x2194, // ↔ East-West route
    0x2195, // ↕ North-South route
    0x21b5, // ↵ Return/checkpoint

    // === STATUS MARKERS ===
    0x2605, // ★ Star (important location)
    0x2606, // ☆ Empty star (discovered)
    0x2713, // ✓ Check (completed/safe)
    0x2717, // ✗ X mark (danger/blocked)
    0x26a0, // ⚠ Warning triangle
    0x2620, // ☠ Skull (extreme danger)
    0x2764, // ❤ Heart (shelter/safety)

    // === NATURAL FEATURES ===
    0x2248, // ≈ Water/waves
    0x2261, // ≡ Horizontal lines (path/road)
    0x00b7, // · Dot (sand/desert)
    0x2022, // • Bullet (forest dot)
    0x2591, // ░ Light shade (sparse vegetation)
    0x2592, // ▒ Medium shade (dense vegetation)
    0x2593, // ▓ Dark shade (impassable)

    // === RESOURCES ===
    0x2302, // ⌂ House (shelter)
    0x263c, // ☼ Sun (solar/energy)
    0x2602, // ☂ Umbrella (rain shelter)
    0x2668, // ♨ Hot springs (heat source)
    0x266a, // ♪ Note (signal/radio)
  ],
  asciiMapping: {
    // Terrain
    0x25b2: "^",
    0x25bc: "v",
    0x25c6: "<>",
    0x25cf: "O",
    0x25cb: "o",
    0x25a0: "#",
    0x25a1: "[]",
    // Directional
    0x2190: "<-",
    0x2191: "^",
    0x2192: "->",
    0x2193: "v",
    0x2194: "<>",
    0x2195: "^v",
    0x21b5: "R",
    // Status
    0x2605: "*",
    0x2606: "*",
    0x2713: "Y",
    0x2717: "X",
    0x26a0: "!",
    0x2620: "X",
    0x2764: "<3",
    // Natural
    0x2248: "~",
    0x2261: "=",
    0x00b7: ".",
    0x2022: ".",
    0x2591: ".",
    0x2592: ":",
    0x2593: "%",
    // Resources
    0x2302: "H",
    0x263c: "*",
    0x2602: "U",
    0x2668: "~",
    0x266a: "J",
  },
};

/**
 * All available character sets
 */
export const CHARACTER_DATASETS = [
  ASCII_PRINTABLE,
  TELETEXT_BLOCK_GRAPHICS,
  BOX_DRAWING,
  MAP_SYMBOLS,
  EMOJI_COLOR_FULL,
  EMOJI_MONO_FULL,
];

/**
 * Get ASCII mapping for a character code
 */
export function getAsciiMapping(code: number, dataset?: CharacterSet): string {
  // Check specific dataset first
  if (dataset?.asciiMapping?.[code]) {
    return dataset.asciiMapping[code];
  }

  // Check all datasets
  for (const ds of CHARACTER_DATASETS) {
    if (ds.asciiMapping?.[code]) {
      return ds.asciiMapping[code];
    }
  }

  // Default to the character itself if in ASCII printable range
  if (code >= 32 && code <= 126) {
    return String.fromCharCode(code);
  }

  // Default fallback
  return "?";
}

/**
 * Find which dataset a character belongs to
 */
export function findDatasetForCode(code: number): CharacterSet | null {
  for (const dataset of CHARACTER_DATASETS) {
    if (dataset.codes.includes(code)) {
      return dataset;
    }
  }
  return null;
}
