# KDT Placer

A KiCad plugin for placing keyboard switch footprints from [Keyboard Design Toolkit](https://github.com/keyboard-design-toolkit) JSON exports.

## Overview

KDT Placer bridges the gap between modern keyboard layout design and PCB creation. While [Keyboard Layout Editor (KLE)](http://www.keyboard-layout-editor.com/) has long been the standard for keyboard design with [kb-placer](https://github.com/yskoht/keyboard-layout-editor-placer) handling KiCad placement, Keyboard Design Toolkit (KDT) represents the next generation of keyboard editing tools.

**Why KDT Placer?**

KDT uses ReactFlow for its layout editor, outputting absolute-positioned components in JSON format—a fundamentally different approach from KLE's relative positioning. This means KLE-based placement tools like kb-placer aren't compatible with KDT exports. KDT Placer fills this gap, enabling a complete KDT → KiCad workflow.

## Features

- **JSON Layout Import**: Reads ReactFlow JSON format directly from KDT
- **Automatic Switch Placement**: Places switch footprints with precise positioning and rotation
- **Associated Component Placement**: Configurable placement of diodes, LEDs, and other per-key components
- **Flexible Positioning**: Custom X/Y key spacing and pixel-to-mm scaling
- **Rotation Support**: Handles rotated keys with automatic offset calculations
- **Multi-layer Support**: Place components on front or back PCB layers
- **Settings Persistence**: Saves your configuration between sessions

## Installation

Copy the plugin files to your KiCad scripting plugins directory:

| Platform | Path |
|----------|------|
| Linux | `~/.local/share/kicad/8.0/scripting/plugins/kdt-placer/` |
| macOS | `~/Library/Preferences/kicad/8.0/scripting/plugins/kdt-placer/` |
| Windows | `%APPDATA%/kicad/8.0/scripting/plugins/kdt-placer/` |

Replace `8.0` with your KiCad version (e.g., `7.0` for KiCad 7.x).

## Usage

1. Design your keyboard layout in Keyboard Design Toolkit and export as JSON
2. Open your PCB in KiCad's PCB Editor
3. Go to **Tools → External Plugins → KDT Placer**
4. Select your JSON file and configure placement settings
5. Click **Place Footprints**

The plugin will place all switch footprints and associated components, then display a summary of results.

## Configuration

### Main Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Step X/Y (mm) | Key unit spacing | 19.05mm (standard 1U) |
| Reference Unit Size (px) | Pixel-to-mm scaling factor | 60px |

### Component Settings

For switches, diodes, and additional components:

- **Annotation Pattern**: Naming template (e.g., `SW{}` → SW1, SW2)
- **X/Y Offset**: Position relative to switch center (mm)
- **Orientation**: Rotation in degrees
- **PCB Side**: Front or back layer

Settings are automatically saved to `~/.config/kdt-placer/settings.json`.

## Supported JSON Formats

KDT Placer supports multiple JSON structures from KDT exports:

- `data.layout.nodes` (standard KDT format)
- `data.nodes` (alternative structure)
- Direct array of nodes

Each node should contain position data (`x`, `y`), dimensions (`widthU`, `heightU`), and optional rotation information.

## License

MIT
