"""
KDT Placer - KiCad Plugin for Keyboard Design Toolkit

This plugin reads ReactFlow JSON from Keyboard Design Toolkit and places
switch footprints (plus associated diodes and additional components)
according to the layout.

Installation:
    Copy this folder to your KiCad plugins directory:
    - Linux: ~/.local/share/kicad/8.0/scripting/plugins/
    - macOS: ~/Library/Preferences/kicad/8.0/scripting/plugins/
    - Windows: %APPDATA%/kicad/8.0/scripting/plugins/

    For KiCad 7.x, replace "8.0" with "7.0" in the paths above.

Usage:
    1. Open your PCB in KiCad's PCB Editor
    2. Go to Tools > External Plugins > KDT Placer
    3. Select your KDT JSON file and configure placement settings
    4. Click "Place Footprints"
"""

from .kdt_placer_action import KDTPlacerAction


def register():
    """Register the plugin with KiCad."""
    KDTPlacerAction().register()


# Auto-register when imported by KiCad
register()
