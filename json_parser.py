"""
JSON parser for ReactFlow layout data from Keyboard Design Toolkit.
Extracts key positions, sizes, and rotation information.
"""

import json
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class KeyData:
    """Represents a parsed key from the JSON layout."""
    label: str
    center_x: float  # Center position in pixels
    center_y: float  # Center position in pixels
    width_u: float   # Width in key units
    height_u: float  # Height in key units
    rotation: float  # Rotation in degrees
    rotation_origin_x: float  # 0-1, relative to key bounds
    rotation_origin_y: float  # 0-1, relative to key bounds


def parse_kdt_json(json_path: str) -> List[KeyData]:
    """
    Parse a KDT ReactFlow JSON file and extract key data.

    Args:
        json_path: Path to the JSON file

    Returns:
        List of KeyData objects representing each key

    Raises:
        ValueError: If JSON structure is invalid
        FileNotFoundError: If file doesn't exist
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    return parse_kdt_data(data)


def parse_kdt_data(data: dict) -> List[KeyData]:
    """
    Parse KDT data from a dictionary.

    Args:
        data: Parsed JSON dictionary

    Returns:
        List of KeyData objects

    Raises:
        ValueError: If data structure is invalid
    """
    if 'layout' not in data:
        raise ValueError("JSON must contain 'layout' key")

    layout = data['layout']
    if 'nodes' not in layout:
        raise ValueError("Layout must contain 'nodes' array")

    keys = []
    for node in layout['nodes']:
        key = parse_node(node)
        if key is not None:
            keys.append(key)

    return keys


def parse_node(node: dict) -> Optional[KeyData]:
    """
    Parse a single node from the ReactFlow layout.

    Args:
        node: Node dictionary from the JSON

    Returns:
        KeyData object or None if node is invalid/not a key
    """
    # Validate required fields
    if 'position' not in node:
        return None
    if 'data' not in node:
        return None

    position = node['position']
    data = node['data']

    # Get position (top-left corner in pixels)
    x = float(position.get('x', 0))
    y = float(position.get('y', 0))

    # Get dimensions in pixels
    width_px = float(node.get('width', 60))
    height_px = float(node.get('height', 60))

    # Calculate center position
    center_x = x + width_px / 2
    center_y = y + height_px / 2

    # Get label (required for annotation mapping)
    label = data.get('label')
    if label is None:
        return None
    label = str(label)

    # Get key dimensions in units
    width_u = float(data.get('widthU', 1))
    height_u = float(data.get('heightU', 1))

    # Get rotation info
    rotation = float(data.get('rotation', 0))
    rotation_origin_x = float(data.get('rotationOriginX', 0.5))
    rotation_origin_y = float(data.get('rotationOriginY', 0.5))

    return KeyData(
        label=label,
        center_x=center_x,
        center_y=center_y,
        width_u=width_u,
        height_u=height_u,
        rotation=rotation,
        rotation_origin_x=rotation_origin_x,
        rotation_origin_y=rotation_origin_y
    )


def validate_json_structure(json_path: str) -> tuple[bool, str]:
    """
    Validate that a JSON file has the expected KDT structure.

    Args:
        json_path: Path to the JSON file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, f"File not found: {json_path}"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    if 'layout' not in data:
        return False, "JSON must contain 'layout' key"

    layout = data['layout']
    if 'nodes' not in layout:
        return False, "Layout must contain 'nodes' array"

    nodes = layout['nodes']
    if not isinstance(nodes, list):
        return False, "'nodes' must be an array"

    if len(nodes) == 0:
        return False, "No nodes found in layout"

    # Check at least one valid key exists
    valid_keys = 0
    for node in nodes:
        if 'position' in node and 'data' in node:
            if 'label' in node.get('data', {}):
                valid_keys += 1

    if valid_keys == 0:
        return False, "No valid key nodes found (nodes must have position, data, and data.label)"

    return True, f"Valid JSON with {valid_keys} keys"
