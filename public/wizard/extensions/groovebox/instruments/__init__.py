"""
Groovebox Instruments Module
============================

TR-808 drums, TB-303 bass, 80s synths, and retro SFX.
"""

from .drum_808 import Drum808, DrumSound, GM_DRUM_MAP

from .bass_303 import (
    Bass303,
    Pattern303,
    Note303,
    Waveform,
    Filter303,
    Envelope303,
    create_acid_pattern,
    create_techno_pattern,
    parse_bass_mml,
)

from .synth_80s import (
    Synth80s,
    SynthType,
    SynthPatch,
    SynthNote,
    ADSR,
    LFO,
    Chorus,
    create_juno_pad,
    create_dx7_epiano,
    create_dx7_bells,
    create_prophet_lead,
    create_prophet_brass,
    get_preset,
    list_presets,
    PRESETS,
)

__all__ = [
    # 808 Drums
    "Drum808",
    "DrumSound",
    "GM_DRUM_MAP",
    # 303 Bass
    "Bass303",
    "Pattern303",
    "Note303",
    "Waveform",
    "Filter303",
    "Envelope303",
    "create_acid_pattern",
    "create_techno_pattern",
    "parse_bass_mml",
    # 80s Synth
    "Synth80s",
    "SynthType",
    "SynthPatch",
    "SynthNote",
    "ADSR",
    "LFO",
    "Chorus",
    "create_juno_pad",
    "create_dx7_epiano",
    "create_dx7_bells",
    "create_prophet_lead",
    "create_prophet_brass",
    "get_preset",
    "list_presets",
    "PRESETS",
]
