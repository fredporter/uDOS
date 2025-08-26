#!/bin/bash
# uDOS v1.0.4.1 Polaroid Color System
# Centralized color management using tput for maximum terminal compatibility
# Based on classic Polaroid instant camera aesthetic

# Initialize color support detection
init_polaroid_colors() {
    # Source display capabilities first
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$script_dir/display/glyph-detector.sh" ]]; then
        source "$script_dir/display/glyph-detector.sh"
    fi

    # Set colors based on terminal capabilities
    if [[ "${UDOS_COLORS:-mono}" == "256" ]]; then
        # 256-color mode - Full Polaroid palette
        readonly POLAROID_ORANGE_POP="$(tput setaf 203)"     # Orange Pop (Polaroid signature)
        readonly POLAROID_LIME_GLOW="$(tput setaf 154)"      # Lime Glow
        readonly POLAROID_CYAN_FLASH="$(tput setaf 33)"      # Cyan Flash
        readonly POLAROID_MAGENTA_BUZZ="$(tput setaf 199)"   # Magenta Buzz
        readonly POLAROID_YELLOW_BURST="$(tput setaf 226)"   # Yellow Burst
        readonly POLAROID_BLUE_CHILL="$(tput setaf 39)"      # Blue Chill
        readonly POLAROID_RED_HOT="$(tput setaf 196)"        # Red Hot
        readonly POLAROID_GREEN_FADE="$(tput setaf 85)"      # Green Fade

        # Legacy aliases for compatibility
        readonly RED="$POLAROID_ORANGE_POP"
        readonly GREEN="$POLAROID_LIME_GLOW"
        readonly BLUE="$POLAROID_CYAN_FLASH"
        readonly YELLOW="$POLAROID_YELLOW_BURST"
        readonly PURPLE="$POLAROID_MAGENTA_BUZZ"
        readonly CYAN="$POLAROID_BLUE_CHILL"

    elif [[ "${UDOS_COLORS:-mono}" == "16" ]]; then
        # 16-color mode - Basic color mapping
        readonly POLAROID_ORANGE_POP="$(tput setaf 9)"       # Bright red
        readonly POLAROID_LIME_GLOW="$(tput setaf 10)"       # Bright green
        readonly POLAROID_CYAN_FLASH="$(tput setaf 14)"      # Bright cyan
        readonly POLAROID_MAGENTA_BUZZ="$(tput setaf 13)"    # Bright magenta
        readonly POLAROID_YELLOW_BURST="$(tput setaf 11)"    # Bright yellow
        readonly POLAROID_BLUE_CHILL="$(tput setaf 12)"      # Bright blue

        # Legacy aliases
        readonly RED="$(tput setaf 1)"
        readonly GREEN="$(tput setaf 2)"
        readonly BLUE="$(tput setaf 4)"
        readonly YELLOW="$(tput setaf 3)"
        readonly PURPLE="$(tput setaf 5)"
        readonly CYAN="$(tput setaf 6)"

    else
        # Monochrome/basic mode - No colors
        readonly POLAROID_ORANGE_POP=""
        readonly POLAROID_LIME_GLOW=""
        readonly POLAROID_CYAN_FLASH=""
        readonly POLAROID_MAGENTA_BUZZ=""
        readonly POLAROID_YELLOW_BURST=""
        readonly POLAROID_BLUE_CHILL=""

        # Legacy aliases (empty)
        readonly RED=""
        readonly GREEN=""
        readonly BLUE=""
        readonly YELLOW=""
        readonly PURPLE=""
        readonly CYAN=""
    fi

    # Common formatting (works in all modes)
    readonly BOLD="$(tput bold 2>/dev/null || echo '')"
    readonly DIM="$(tput dim 2>/dev/null || echo '')"
    readonly UNDERLINE="$(tput smul 2>/dev/null || echo '')"
    readonly BLINK="$(tput blink 2>/dev/null || echo '')"
    readonly REVERSE="$(tput rev 2>/dev/null || echo '')"
    readonly RESET="$(tput sgr0 2>/dev/null || echo '')"
    readonly NC="$RESET"  # Legacy alias
    readonly WHITE="$(tput setaf 7 2>/dev/null || echo '')"

    # Export for use in other scripts
    export POLAROID_ORANGE_POP POLAROID_LIME_GLOW POLAROID_CYAN_FLASH
    export POLAROID_MAGENTA_BUZZ POLAROID_YELLOW_BURST POLAROID_BLUE_CHILL
    export POLAROID_RED_HOT POLAROID_GREEN_FADE
    export RED GREEN BLUE YELLOW PURPLE CYAN WHITE
    export BOLD DIM UNDERLINE BLINK REVERSE RESET NC
    export UDOS_POLAROID_INITIALIZED=1
}

# Color utility functions
polaroid_echo() {
    local color="$1"
    shift
    case "$color" in
        "orange"|"red") echo -e "${POLAROID_ORANGE_POP}$*${RESET}" ;;
        "lime"|"green") echo -e "${POLAROID_LIME_GLOW}$*${RESET}" ;;
        "cyan"|"blue") echo -e "${POLAROID_CYAN_FLASH}$*${RESET}" ;;
        "magenta"|"purple") echo -e "${POLAROID_MAGENTA_BUZZ}$*${RESET}" ;;
        "yellow") echo -e "${POLAROID_YELLOW_BURST}$*${RESET}" ;;
        "chill") echo -e "${POLAROID_BLUE_CHILL}$*${RESET}" ;;
        "bold") echo -e "${BOLD}$*${RESET}" ;;
        "dim") echo -e "${DIM}$*${RESET}" ;;
        *) echo -e "$*" ;;
    esac
}

# Initialize colors when sourced
if [[ "${UDOS_POLAROID_INITIALIZED:-0}" != "1" ]]; then
    init_polaroid_colors
fi
