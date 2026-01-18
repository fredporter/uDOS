"""
Font Manager API Routes
Serves font collections and character data
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List

router = APIRouter(prefix="/api/v1/fonts", tags=["fonts"])

# Comprehensive character collections
COLLECTIONS = {
    "emoji": {
        "name": "emoji",
        "family": "Noto Color Emoji",
        "style": "Regular",
        "description": "Color emoji for expressions, objects, and symbols",
        "characters": [
            # Smileys & Emotion (expanded set)
            {"codepoint": 0x1F600, "name": "grinning face", "category": "smileys", "utf8": "😀"},
            {"codepoint": 0x1F601, "name": "beaming face with smiling eyes", "category": "smileys", "utf8": "😁"},
            {"codepoint": 0x1F602, "name": "face with tears of joy", "category": "smileys", "utf8": "😂"},
            {"codepoint": 0x1F603, "name": "grinning face with big eyes", "category": "smileys", "utf8": "😃"},
            {"codepoint": 0x1F604, "name": "grinning face with smiling eyes", "category": "smileys", "utf8": "😄"},
            {"codepoint": 0x1F605, "name": "grinning face with sweat", "category": "smileys", "utf8": "😅"},
            {"codepoint": 0x1F606, "name": "grinning squinting face", "category": "smileys", "utf8": "😆"},
            {"codepoint": 0x1F607, "name": "smiling face with halo", "category": "smileys", "utf8": "😇"},
            {"codepoint": 0x1F608, "name": "smiling face with horns", "category": "smileys", "utf8": "😈"},
            {"codepoint": 0x1F609, "name": "winking face", "category": "smileys", "utf8": "😉"},
            {"codepoint": 0x1F60A, "name": "smiling face with smiling eyes", "category": "smileys", "utf8": "😊"},
            {"codepoint": 0x1F60B, "name": "face savoring food", "category": "smileys", "utf8": "😋"},
            {"codepoint": 0x1F60C, "name": "relieved face", "category": "smileys", "utf8": "😌"},
            {"codepoint": 0x1F60D, "name": "smiling face with heart-eyes", "category": "smileys", "utf8": "😍"},
            {"codepoint": 0x1F60E, "name": "smiling face with sunglasses", "category": "smileys", "utf8": "😎"},
            {"codepoint": 0x1F60F, "name": "smirking face", "category": "smileys", "utf8": "😏"},
            {"codepoint": 0x1F610, "name": "neutral face", "category": "smileys", "utf8": "😐"},
            {"codepoint": 0x1F611, "name": "expressionless face", "category": "smileys", "utf8": "😑"},
            {"codepoint": 0x1F612, "name": "unamused face", "category": "smileys", "utf8": "😒"},
            {"codepoint": 0x1F613, "name": "downcast face with sweat", "category": "smileys", "utf8": "😓"},
            {"codepoint": 0x1F614, "name": "pensive face", "category": "smileys", "utf8": "😔"},
            {"codepoint": 0x1F615, "name": "confused face", "category": "smileys", "utf8": "😕"},
            {"codepoint": 0x1F616, "name": "confounded face", "category": "smileys", "utf8": "😖"},
            {"codepoint": 0x1F62C, "name": "grimacing face", "category": "smileys", "utf8": "😬"},
            {"codepoint": 0x1F62D, "name": "loudly crying face", "category": "smileys", "utf8": "😭"},
            {"codepoint": 0x1F631, "name": "face screaming in fear", "category": "smileys", "utf8": "😱"},
            {"codepoint": 0x1F642, "name": "slightly smiling face", "category": "smileys", "utf8": "🙂"},
            {"codepoint": 0x1F643, "name": "upside-down face", "category": "smileys", "utf8": "🙃"},
            {"codepoint": 0x1F910, "name": "zipper-mouth face", "category": "smileys", "utf8": "🤐"},
            {"codepoint": 0x1F911, "name": "money-mouth face", "category": "smileys", "utf8": "🤑"},
            # Animals & Nature
            {"codepoint": 0x1F436, "name": "dog face", "category": "animals", "utf8": "🐶"},
            {"codepoint": 0x1F431, "name": "cat face", "category": "animals", "utf8": "🐱"},
            {"codepoint": 0x1F42D, "name": "mouse face", "category": "animals", "utf8": "🐭"},
            {"codepoint": 0x1F430, "name": "rabbit face", "category": "animals", "utf8": "🐰"},
            {"codepoint": 0x1F98A, "name": "fox", "category": "animals", "utf8": "🦊"},
            {"codepoint": 0x1F43B, "name": "bear", "category": "animals", "utf8": "🐻"},
            {"codepoint": 0x1F43C, "name": "panda", "category": "animals", "utf8": "🐼"},
            {"codepoint": 0x1F428, "name": "koala", "category": "animals", "utf8": "🐨"},
            {"codepoint": 0x1F42F, "name": "tiger face", "category": "animals", "utf8": "🐯"},
            {"codepoint": 0x1F981, "name": "lion", "category": "animals", "utf8": "🦁"},
            {"codepoint": 0x1F434, "name": "horse face", "category": "animals", "utf8": "🐴"},
            {"codepoint": 0x1F984, "name": "unicorn", "category": "animals", "utf8": "🦄"},
            # Food & Drink
            {"codepoint": 0x1F34E, "name": "red apple", "category": "food", "utf8": "🍎"},
            {"codepoint": 0x1F34A, "name": "tangerine", "category": "food", "utf8": "🍊"},
            {"codepoint": 0x1F34C, "name": "banana", "category": "food", "utf8": "🍌"},
            {"codepoint": 0x1F347, "name": "grapes", "category": "food", "utf8": "🍇"},
            {"codepoint": 0x1F353, "name": "strawberry", "category": "food", "utf8": "🍓"},
            {"codepoint": 0x1F349, "name": "watermelon", "category": "food", "utf8": "🍉"},
            {"codepoint": 0x1F351, "name": "peach", "category": "food", "utf8": "🍑"},
            {"codepoint": 0x1F352, "name": "cherries", "category": "food", "utf8": "🍒"},
            {"codepoint": 0x1F95D, "name": "kiwi fruit", "category": "food", "utf8": "🥝"},
            {"codepoint": 0x1F345, "name": "tomato", "category": "food", "utf8": "🍅"},
            {"codepoint": 0x1F354, "name": "hamburger", "category": "food", "utf8": "🍔"},
            {"codepoint": 0x1F355, "name": "pizza", "category": "food", "utf8": "🍕"},
            # Activities & Objects
            {"codepoint": 0x26BD, "name": "soccer ball", "category": "activities", "utf8": "⚽"},
            {"codepoint": 0x1F3C0, "name": "basketball", "category": "activities", "utf8": "🏀"},
            {"codepoint": 0x1F3C8, "name": "american football", "category": "activities", "utf8": "🏈"},
            {"codepoint": 0x26BE, "name": "baseball", "category": "activities", "utf8": "⚾"},
            {"codepoint": 0x1F3BE, "name": "tennis", "category": "activities", "utf8": "🎾"},
            {"codepoint": 0x1F3D0, "name": "volleyball", "category": "activities", "utf8": "🏐"},
            {"codepoint": 0x1F3C9, "name": "rugby football", "category": "activities", "utf8": "🏉"},
            {"codepoint": 0x1F94E, "name": "softball", "category": "activities", "utf8": "🥎"},
            {"codepoint": 0x1F3B1, "name": "pool 8 ball", "category": "activities", "utf8": "🎱"},
            {"codepoint": 0x1F3AE, "name": "video game", "category": "activities", "utf8": "🎮"},
            {"codepoint": 0x1F3AF, "name": "direct hit", "category": "activities", "utf8": "🎯"},
            {"codepoint": 0x1F3B2, "name": "game die", "category": "activities", "utf8": "🎲"},
        ]
    },
    "symbols": {
        "name": "symbols",
        "family": "Unicode Symbols",
        "style": "Regular",
        "characters": [
            # Math & Logic
            {"codepoint": 0x002B, "name": "plus sign", "category": "math", "utf8": "+"},
            {"codepoint": 0x002D, "name": "minus sign", "category": "math", "utf8": "-"},
            {"codepoint": 0x00D7, "name": "multiplication sign", "category": "math", "utf8": "×"},
            {"codepoint": 0x00F7, "name": "division sign", "category": "math", "utf8": "÷"},
            {"codepoint": 0x003D, "name": "equals sign", "category": "math", "utf8": "="},
            {"codepoint": 0x2260, "name": "not equal to", "category": "math", "utf8": "≠"},
            {"codepoint": 0x003C, "name": "less-than sign", "category": "math", "utf8": "<"},
            {"codepoint": 0x003E, "name": "greater-than sign", "category": "math", "utf8": ">"},
            {"codepoint": 0x2264, "name": "less-than or equal to", "category": "math", "utf8": "≤"},
            {"codepoint": 0x2265, "name": "greater-than or equal to", "category": "math", "utf8": "≥"},
            # Arrows
            {"codepoint": 0x2190, "name": "leftwards arrow", "category": "arrows", "utf8": "←"},
            {"codepoint": 0x2191, "name": "upwards arrow", "category": "arrows", "utf8": "↑"},
            {"codepoint": 0x2192, "name": "rightwards arrow", "category": "arrows", "utf8": "→"},
            {"codepoint": 0x2193, "name": "downwards arrow", "category": "arrows", "utf8": "↓"},
            {"codepoint": 0x2194, "name": "left right arrow", "category": "arrows", "utf8": "↔"},
            {"codepoint": 0x2195, "name": "up down arrow", "category": "arrows", "utf8": "↕"},
            {"codepoint": 0x21D0, "name": "leftwards double arrow", "category": "arrows", "utf8": "⇐"},
            {"codepoint": 0x21D2, "name": "rightwards double arrow", "category": "arrows", "utf8": "⇒"},
            {"codepoint": 0x21D4, "name": "left right double arrow", "category": "arrows", "utf8": "⇔"},
            # Geometric Shapes
            {"codepoint": 0x25A0, "name": "black square", "category": "shapes", "utf8": "■"},
            {"codepoint": 0x25A1, "name": "white square", "category": "shapes", "utf8": "□"},
            {"codepoint": 0x25B2, "name": "black up-pointing triangle", "category": "shapes", "utf8": "▲"},
            {"codepoint": 0x25BC, "name": "black down-pointing triangle", "category": "shapes", "utf8": "▼"},
            {"codepoint": 0x25C6, "name": "black diamond", "category": "shapes", "utf8": "◆"},
            {"codepoint": 0x25C7, "name": "white diamond", "category": "shapes", "utf8": "◇"},
            {"codepoint": 0x25CF, "name": "black circle", "category": "shapes", "utf8": "●"},
            {"codepoint": 0x25CB, "name": "white circle", "category": "shapes", "utf8": "○"},
            {"codepoint": 0x2605, "name": "black star", "category": "shapes", "utf8": "★"},
            {"codepoint": 0x2606, "name": "white star", "category": "shapes", "utf8": "☆"},
            # Checkmarks & Crosses
            {"codepoint": 0x2713, "name": "check mark", "category": "symbols", "utf8": "✓"},
            {"codepoint": 0x2714, "name": "heavy check mark", "category": "symbols", "utf8": "✔"},
            {"codepoint": 0x2717, "name": "ballot x", "category": "symbols", "utf8": "✗"},
            {"codepoint": 0x2718, "name": "heavy ballot x", "category": "symbols", "utf8": "✘"},
        ]
    },
    "box": {
        "name": "box",
        "family": "Box Drawing",
        "style": "Regular",
        "characters": [
            # Box Drawing Characters
            {"codepoint": 0x2500, "name": "box drawings light horizontal", "category": "box", "utf8": "─"},
            {"codepoint": 0x2501, "name": "box drawings heavy horizontal", "category": "box", "utf8": "━"},
            {"codepoint": 0x2502, "name": "box drawings light vertical", "category": "box", "utf8": "│"},
            {"codepoint": 0x2503, "name": "box drawings heavy vertical", "category": "box", "utf8": "┃"},
            {"codepoint": 0x250C, "name": "box drawings light down and right", "category": "box", "utf8": "┌"},
            {"codepoint": 0x250F, "name": "box drawings heavy down and right", "category": "box", "utf8": "┏"},
            {"codepoint": 0x2510, "name": "box drawings light down and left", "category": "box", "utf8": "┐"},
            {"codepoint": 0x2513, "name": "box drawings heavy down and left", "category": "box", "utf8": "┓"},
            {"codepoint": 0x2514, "name": "box drawings light up and right", "category": "box", "utf8": "└"},
            {"codepoint": 0x2517, "name": "box drawings heavy up and right", "category": "box", "utf8": "┗"},
            {"codepoint": 0x2518, "name": "box drawings light up and left", "category": "box", "utf8": "┘"},
            {"codepoint": 0x251B, "name": "box drawings heavy up and left", "category": "box", "utf8": "┛"},
            {"codepoint": 0x251C, "name": "box drawings light vertical and right", "category": "box", "utf8": "├"},
            {"codepoint": 0x2524, "name": "box drawings light vertical and left", "category": "box", "utf8": "┤"},
            {"codepoint": 0x252C, "name": "box drawings light down and horizontal", "category": "box", "utf8": "┬"},
            {"codepoint": 0x2534, "name": "box drawings light up and horizontal", "category": "box", "utf8": "┴"},
            {"codepoint": 0x253C, "name": "box drawings light vertical and horizontal", "category": "box", "utf8": "┼"},
            # Block Elements
            {"codepoint": 0x2580, "name": "upper half block", "category": "blocks", "utf8": "▀"},
            {"codepoint": 0x2584, "name": "lower half block", "category": "blocks", "utf8": "▄"},
            {"codepoint": 0x2588, "name": "full block", "category": "blocks", "utf8": "█"},
            {"codepoint": 0x258C, "name": "left half block", "category": "blocks", "utf8": "▌"},
            {"codepoint": 0x2590, "name": "right half block", "category": "blocks", "utf8": "▐"},
            {"codepoint": 0x2591, "name": "light shade", "category": "blocks", "utf8": "░"},
            {"codepoint": 0x2592, "name": "medium shade", "category": "blocks", "utf8": "▒"},
            {"codepoint": 0x2593, "name": "dark shade", "category": "blocks", "utf8": "▓"},
        ]
    },
    "teletext": {
        "name": "teletext",
        "family": "Teletext Blocks",
        "style": "2×3 Mosaic",
        "description": "Complete set of 2×3 teletext blocks for mosaic graphics (64 combinations)",
        "characters": [
            # Legacy Computing Sextants (U+1FB00 to U+1FB3B)
            # Full 2×3 block grid patterns (64 base patterns)
            {"codepoint": 0x1FB00, "name": "block sextant-1", "category": "teletext", "utf8": "🬀"},
            {"codepoint": 0x1FB01, "name": "block sextant-2", "category": "sextant", "utf8": "🬁"},
            {"codepoint": 0x1FB02, "name": "block sextant-12", "category": "sextant", "utf8": "🬂"},
            {"codepoint": 0x1FB03, "name": "block sextant-3", "category": "sextant", "utf8": "🬃"},
            {"codepoint": 0x1FB04, "name": "block sextant-13", "category": "sextant", "utf8": "🬄"},
            {"codepoint": 0x1FB05, "name": "block sextant-23", "category": "sextant", "utf8": "🬅"},
            {"codepoint": 0x1FB06, "name": "block sextant-123", "category": "sextant", "utf8": "🬆"},
            {"codepoint": 0x1FB07, "name": "block sextant-4", "category": "sextant", "utf8": "🬇"},
            {"codepoint": 0x1FB08, "name": "block sextant-14", "category": "sextant", "utf8": "🬈"},
            {"codepoint": 0x1FB09, "name": "block sextant-24", "category": "sextant", "utf8": "🬉"},
            {"codepoint": 0x1FB0A, "name": "block sextant-124", "category": "sextant", "utf8": "🬊"},
            {"codepoint": 0x1FB0B, "name": "block sextant-34", "category": "sextant", "utf8": "🬋"},
            {"codepoint": 0x1FB0C, "name": "block sextant-134", "category": "sextant", "utf8": "🬌"},
            {"codepoint": 0x1FB0D, "name": "block sextant-234", "category": "sextant", "utf8": "🬍"},
            {"codepoint": 0x1FB0E, "name": "block sextant-1234", "category": "sextant", "utf8": "🬎"},
            {"codepoint": 0x1FB0F, "name": "block sextant-5", "category": "sextant", "utf8": "🬏"},
            {"codepoint": 0x1FB10, "name": "block sextant-15", "category": "sextant", "utf8": "🬐"},
            {"codepoint": 0x1FB11, "name": "block sextant-25", "category": "sextant", "utf8": "🬑"},
            {"codepoint": 0x1FB12, "name": "block sextant-125", "category": "sextant", "utf8": "🬒"},
            {"codepoint": 0x1FB13, "name": "block sextant-35", "category": "sextant", "utf8": "🬓"},
            {"codepoint": 0x1FB14, "name": "block sextant-235", "category": "sextant", "utf8": "🬔"},
            {"codepoint": 0x1FB15, "name": "block sextant-1235", "category": "sextant", "utf8": "🬕"},
            {"codepoint": 0x1FB16, "name": "block sextant-45", "category": "sextant", "utf8": "🬖"},
            {"codepoint": 0x1FB17, "name": "block sextant-145", "category": "sextant", "utf8": "🬗"},
            {"codepoint": 0x1FB18, "name": "block sextant-245", "category": "sextant", "utf8": "🬘"},
            {"codepoint": 0x1FB19, "name": "block sextant-1245", "category": "sextant", "utf8": "🬙"},
            {"codepoint": 0x1FB1A, "name": "block sextant-345", "category": "sextant", "utf8": "🬚"},
            {"codepoint": 0x1FB1B, "name": "block sextant-1345", "category": "sextant", "utf8": "🬛"},
            {"codepoint": 0x1FB1C, "name": "block sextant-2345", "category": "sextant", "utf8": "🬜"},
            {"codepoint": 0x1FB1D, "name": "block sextant-12345", "category": "sextant", "utf8": "🬝"},
            {"codepoint": 0x1FB1E, "name": "block sextant-6", "category": "sextant", "utf8": "🬞"},
            {"codepoint": 0x1FB1F, "name": "block sextant-16", "category": "sextant", "utf8": "🬟"},
            {"codepoint": 0x1FB20, "name": "block sextant-26", "category": "sextant", "utf8": "🬠"},
            {"codepoint": 0x1FB21, "name": "block sextant-126", "category": "sextant", "utf8": "🬡"},
            {"codepoint": 0x1FB22, "name": "block sextant-36", "category": "sextant", "utf8": "🬢"},
            {"codepoint": 0x1FB23, "name": "block sextant-136", "category": "sextant", "utf8": "🬣"},
            {"codepoint": 0x1FB24, "name": "block sextant-236", "category": "sextant", "utf8": "🬤"},
            {"codepoint": 0x1FB25, "name": "block sextant-1236", "category": "sextant", "utf8": "🬥"},
            {"codepoint": 0x1FB26, "name": "block sextant-46", "category": "sextant", "utf8": "🬦"},
            {"codepoint": 0x1FB27, "name": "block sextant-146", "category": "sextant", "utf8": "🬧"},
            {"codepoint": 0x1FB28, "name": "block sextant-246", "category": "sextant", "utf8": "🬨"},
            {"codepoint": 0x1FB29, "name": "block sextant-1246", "category": "sextant", "utf8": "🬩"},
            {"codepoint": 0x1FB2A, "name": "block sextant-346", "category": "sextant", "utf8": "🬪"},
            {"codepoint": 0x1FB2B, "name": "block sextant-1346", "category": "sextant", "utf8": "🬫"},
            {"codepoint": 0x1FB2C, "name": "block sextant-2346", "category": "sextant", "utf8": "🬬"},
            {"codepoint": 0x1FB2D, "name": "block sextant-12346", "category": "sextant", "utf8": "🬭"},
            {"codepoint": 0x1FB2E, "name": "block sextant-56", "category": "sextant", "utf8": "🬮"},
            {"codepoint": 0x1FB2F, "name": "block sextant-156", "category": "sextant", "utf8": "🬯"},
            {"codepoint": 0x1FB30, "name": "block sextant-256", "category": "sextant", "utf8": "🬰"},
            {"codepoint": 0x1FB31, "name": "block sextant-1256", "category": "sextant", "utf8": "🬱"},
            {"codepoint": 0x1FB32, "name": "block sextant-356", "category": "sextant", "utf8": "🬲"},
            {"codepoint": 0x1FB33, "name": "block sextant-1356", "category": "sextant", "utf8": "🬳"},
            {"codepoint": 0x1FB34, "name": "block sextant-2356", "category": "sextant", "utf8": "🬴"},
            {"codepoint": 0x1FB35, "name": "block sextant-12356", "category": "sextant", "utf8": "🬵"},
            {"codepoint": 0x1FB36, "name": "block sextant-456", "category": "sextant", "utf8": "🬶"},
            {"codepoint": 0x1FB37, "name": "block sextant-1456", "category": "sextant", "utf8": "🬷"},
            {"codepoint": 0x1FB38, "name": "block sextant-2456", "category": "sextant", "utf8": "🬸"},
            {"codepoint": 0x1FB39, "name": "block sextant-12456", "category": "sextant", "utf8": "🬹"},
            {"codepoint": 0x1FB3A, "name": "block sextant-3456", "category": "sextant", "utf8": "🬺"},
            {"codepoint": 0x1FB3B, "name": "block sextant-13456", "category": "sextant", "utf8": "🬻"},
            # Also include classic block elements for compatibility
            {"codepoint": 0x2588, "name": "full block", "category": "blocks", "utf8": "█"},
            {"codepoint": 0x2580, "name": "upper half block", "category": "blocks", "utf8": "▀"},
            {"codepoint": 0x2584, "name": "lower half block", "category": "blocks", "utf8": "▄"},
        ]
    },
    "retro-apple": {
        "name": "retro-apple",
        "family": "Chicago / Monaco",
        "style": "Classic Mac",
        "font_files": ["Chicago.ttf", "ChicagoFLF.ttf", "monaco.ttf", "Sanfrisco.ttf"],
        "characters": [
            # Classic Mac system font characters (ASCII printable + system icons)
            {"codepoint": 0x0020, "name": "space", "category": "ascii", "utf8": " "},
            {"codepoint": 0x0041, "name": "latin capital letter A", "category": "ascii", "utf8": "A"},
            {"codepoint": 0x0061, "name": "latin small letter a", "category": "ascii", "utf8": "a"},
            {"codepoint": 0x0030, "name": "digit zero", "category": "ascii", "utf8": "0"},
            {"codepoint": 0x0031, "name": "digit one", "category": "ascii", "utf8": "1"},
            {"codepoint": 0xF8FF, "name": "apple logo", "category": "mac-symbols", "utf8": ""},
            {"codepoint": 0x2318, "name": "command key symbol", "category": "mac-symbols", "utf8": "⌘"},
            {"codepoint": 0x2325, "name": "option key symbol", "category": "mac-symbols", "utf8": "⌥"},
            {"codepoint": 0x21E7, "name": "shift symbol", "category": "mac-symbols", "utf8": "⇧"},
            {"codepoint": 0x2303, "name": "control symbol", "category": "mac-symbols", "utf8": "⌃"},
        ]
    },
    "retro-c64": {
        "name": "retro-c64",
        "family": "PetMe64",
        "style": "Commodore 64",
        "font_files": ["PetMe64.ttf"],
        "characters": [
            # C64 PETSCII characters (ASCII subset + graphics)
            {"codepoint": 0x0041, "name": "latin capital letter A", "category": "ascii", "utf8": "A"},
            {"codepoint": 0x0061, "name": "latin small letter a", "category": "ascii", "utf8": "a"},
            {"codepoint": 0x0030, "name": "digit zero", "category": "ascii", "utf8": "0"},
            {"codepoint": 0x2588, "name": "full block", "category": "petscii", "utf8": "█"},
            {"codepoint": 0x259A, "name": "quadrant upper left and lower right", "category": "petscii", "utf8": "▚"},
            {"codepoint": 0x2596, "name": "quadrant lower left", "category": "petscii", "utf8": "▖"},
            {"codepoint": 0x2597, "name": "quadrant lower right", "category": "petscii", "utf8": "▗"},
            {"codepoint": 0x2598, "name": "quadrant upper left", "category": "petscii", "utf8": "▘"},
            {"codepoint": 0x259D, "name": "quadrant upper right", "category": "petscii", "utf8": "▝"},
            {"codepoint": 0x2665, "name": "black heart suit", "category": "petscii", "utf8": "♥"},
        ]
    },
    "retro-gaming": {
        "name": "retro-gaming",
        "family": "Press Start 2P",
        "style": "8-bit Arcade",
        "font_files": ["PressStart2P-Regular.ttf"],
        "characters": [
            # 8-bit arcade game characters (ASCII + gaming symbols)
            {"codepoint": 0x0041, "name": "latin capital letter A", "category": "ascii", "utf8": "A"},
            {"codepoint": 0x0061, "name": "latin small letter a", "category": "ascii", "utf8": "a"},
            {"codepoint": 0x0030, "name": "digit zero", "category": "ascii", "utf8": "0"},
            {"codepoint": 0x0031, "name": "digit one", "category": "ascii", "utf8": "1"},
            {"codepoint": 0x2665, "name": "black heart", "category": "gaming", "utf8": "♥"},
            {"codepoint": 0x2666, "name": "black diamond", "category": "gaming", "utf8": "♦"},
            {"codepoint": 0x2663, "name": "black club", "category": "gaming", "utf8": "♣"},
            {"codepoint": 0x2660, "name": "black spade", "category": "gaming", "utf8": "♠"},
            {"codepoint": 0x25B2, "name": "up arrow", "category": "gaming", "utf8": "▲"},
            {"codepoint": 0x25BC, "name": "down arrow", "category": "gaming", "utf8": "▼"},
        ]
    },
    "retro-teletext": {
        "name": "retro-teletext",
        "family": "Teletext50",
        "style": "UK Teletext",
        "font_files": ["Teletext50.otf"],
        "characters": [
            # UK Teletext mosaic graphics (7-segment inspired)
            {"codepoint": 0x0041, "name": "latin capital letter A", "category": "ascii", "utf8": "A"},
            {"codepoint": 0x0061, "name": "latin small letter a", "category": "ascii", "utf8": "a"},
            {"codepoint": 0x0030, "name": "digit zero", "category": "ascii", "utf8": "0"},
            {"codepoint": 0x2588, "name": "full block", "category": "teletext", "utf8": "█"},
            {"codepoint": 0x2580, "name": "upper half block", "category": "teletext", "utf8": "▀"},
            {"codepoint": 0x2584, "name": "lower half block", "category": "teletext", "utf8": "▄"},
            {"codepoint": 0x258C, "name": "left half block", "category": "teletext", "utf8": "▌"},
            {"codepoint": 0x2590, "name": "right half block", "category": "teletext", "utf8": "▐"},
            {"codepoint": 0x2596, "name": "quadrant lower left", "category": "teletext", "utf8": "▖"},
            {"codepoint": 0x2597, "name": "quadrant lower right", "category": "teletext", "utf8": "▗"},
        ]
    }
}


@router.get("/collections")
async def list_collections():
    """List available font collections."""
    return {
        "collections": [
            {
                "name": col["name"],
                "display_name": col["family"],
                "family": col["family"],
                "style": col["style"],
                "count": len(col["characters"]),
                "character_count": len(col["characters"]),
            }
            for col in COLLECTIONS.values()
        ]
    }


@router.get("/characters/{collection}")
async def get_collection_characters(
    collection: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get characters from a font collection."""
    if collection not in COLLECTIONS:
        raise HTTPException(status_code=404, detail="Collection not found")

    chars = COLLECTIONS[collection]["characters"]
    return {
        "collection": collection,
        "total": len(chars),
        "offset": offset,
        "limit": limit,
        "items": chars[offset : offset + limit],
    }


@router.get("/search")
async def search_characters(q: str = Query(..., min_length=1)):
    """Search characters across all collections."""
    query_lower = q.lower()
    results = []

    for col_name, col_data in COLLECTIONS.items():
        for char in col_data["characters"]:
            if query_lower in char["name"].lower() or query_lower in char["category"].lower():
                results.append({
                    **char,
                    "collection": col_name,
                    "family": col_data["family"],
                })

    return {
        "query": q,
        "count": len(results),
        "results": results[:50],  # Limit to 50 results
    }


@router.get("/{collection}/export")
async def export_collection(collection: str, format: str = Query("json")):
    """Export a font collection in specified format."""
    if collection not in COLLECTIONS:
        raise HTTPException(status_code=404, detail="Collection not found")

    from fastapi.responses import JSONResponse

    col_data = COLLECTIONS[collection]
    data = {
        "collection": collection,
        "family": col_data["family"],
        "style": col_data["style"],
        "format": format,
        "character_count": len(col_data["characters"]),
        "characters": col_data["characters"],
    }

    return JSONResponse(content=data)
