"""
Groovebox Plugins Module
========================

External instrument bridges for FluidSynth, LMMS, and VCV Rack.
"""

from .plugin_wrapper import (
    PluginManager,
    PluginType,
    PluginInfo,
    SoundFont,
    RenderJob,
    get_plugin_manager,
    render_midi_with_soundfont,
    check_plugin_status,
)

__all__ = [
    "PluginManager",
    "PluginType",
    "PluginInfo",
    "SoundFont",
    "RenderJob",
    "get_plugin_manager",
    "render_midi_with_soundfont",
    "check_plugin_status",
]
