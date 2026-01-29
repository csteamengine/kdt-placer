"""
Footprint placement logic for KDT Placer.
Handles positioning, rotation, and layer management.
"""

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Import pcbnew - will be available when running in KiCad
try:
    import pcbnew
    PCBNEW_AVAILABLE = True
except ImportError:
    PCBNEW_AVAILABLE = False

from .json_parser import KeyData


@dataclass
class ComponentConfig:
    """Configuration for a component type (switch, diode, LED, etc.)."""
    name: str
    annotation_pattern: str  # e.g., "SW{}" or "D{}"
    x_offset_mm: float = 0.0
    y_offset_mm: float = 0.0
    orientation_deg: float = 0.0
    pcb_side: str = "Top"  # "Top" or "Bottom"
    enabled: bool = True


@dataclass
class PlacementResult:
    """Result of placing a single component."""
    reference: str
    success: bool
    message: str


@dataclass
class PlacementSummary:
    """Summary of all placements."""
    total_keys: int
    placed: List[PlacementResult]
    missing: List[PlacementResult]
    errors: List[PlacementResult]


def rotate_offset(x_offset: float, y_offset: float, angle_deg: float) -> Tuple[float, float]:
    """
    Rotate an offset by the given angle.

    Args:
        x_offset: X offset in mm
        y_offset: Y offset in mm
        angle_deg: Rotation angle in degrees

    Returns:
        Tuple of (rotated_x, rotated_y)
    """
    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return (
        x_offset * cos_a - y_offset * sin_a,
        x_offset * sin_a + y_offset * cos_a
    )


def mm_to_nm(mm: float) -> int:
    """Convert millimeters to nanometers (KiCad internal units)."""
    return int(mm * 1_000_000)


def ensure_on_front(fp) -> bool:
    """
    Ensure footprint is on the front (F.Cu) layer.

    Returns:
        True if footprint was flipped, False if already on front
    """
    if fp.GetLayer() == pcbnew.B_Cu:
        fp.Flip(fp.GetPosition(), False)
        return True
    return False


def ensure_on_back(fp) -> bool:
    """
    Ensure footprint is on the back (B.Cu) layer.

    Returns:
        True if footprint was flipped, False if already on back
    """
    if fp.GetLayer() == pcbnew.F_Cu:
        fp.Flip(fp.GetPosition(), False)
        return True
    return False


class FootprintPlacer:
    """Handles placement of footprints based on KDT key data."""

    def __init__(self, board):
        """
        Initialize the placer.

        Args:
            board: KiCad board object (pcbnew.BOARD)
        """
        self.board = board

    def place_keys(
        self,
        keys: List[KeyData],
        switch_config: ComponentConfig,
        diode_config: Optional[ComponentConfig],
        additional_configs: List[ComponentConfig],
        step_x_mm: float = 19.05,
        step_y_mm: float = 19.05,
        ref_unit_px: float = 60.0,
        offset_x_mm: float = 0.0,
        offset_y_mm: float = 0.0
    ) -> PlacementSummary:
        """
        Place footprints for all keys.

        Args:
            keys: List of parsed key data
            switch_config: Configuration for switch footprints
            diode_config: Configuration for diode footprints (None to disable)
            additional_configs: List of additional component configurations
            step_x_mm: Horizontal key spacing in mm
            step_y_mm: Vertical key spacing in mm
            ref_unit_px: Reference unit size in pixels (for scaling)
            offset_x_mm: X offset to shift entire layout (in mm)
            offset_y_mm: Y offset to shift entire layout (in mm)

        Returns:
            PlacementSummary with results
        """
        placed = []
        missing = []
        errors = []

        for key in keys:
            # Calculate target position in mm (with layout offset applied)
            x_mm = (key.center_x / ref_unit_px) * step_x_mm + offset_x_mm
            y_mm = (key.center_y / ref_unit_px) * step_y_mm + offset_y_mm

            # Place switch
            if switch_config.enabled:
                result = self._place_component(
                    key, switch_config, x_mm, y_mm, 0, 0
                )
                self._categorize_result(result, placed, missing, errors)

            # Place diode
            if diode_config and diode_config.enabled:
                result = self._place_component(
                    key, diode_config, x_mm, y_mm,
                    diode_config.x_offset_mm, diode_config.y_offset_mm
                )
                self._categorize_result(result, placed, missing, errors)

            # Place additional components
            for config in additional_configs:
                if config.enabled:
                    result = self._place_component(
                        key, config, x_mm, y_mm,
                        config.x_offset_mm, config.y_offset_mm
                    )
                    self._categorize_result(result, placed, missing, errors)

        return PlacementSummary(
            total_keys=len(keys),
            placed=placed,
            missing=missing,
            errors=errors
        )

    def _place_component(
        self,
        key: KeyData,
        config: ComponentConfig,
        base_x_mm: float,
        base_y_mm: float,
        x_offset_mm: float,
        y_offset_mm: float
    ) -> PlacementResult:
        """
        Place a single component relative to a key.

        Args:
            key: Key data
            config: Component configuration
            base_x_mm: Base X position (switch center) in mm
            base_y_mm: Base Y position (switch center) in mm
            x_offset_mm: X offset from switch center in mm
            y_offset_mm: Y offset from switch center in mm

        Returns:
            PlacementResult
        """
        # Generate reference from pattern
        reference = config.annotation_pattern.replace("{}", key.label)

        # Find footprint
        fp = self.board.FindFootprintByReference(reference)
        if fp is None:
            return PlacementResult(
                reference=reference,
                success=False,
                message=f"Footprint not found: {reference}"
            )

        try:
            # Calculate offset with key rotation applied
            # Negate rotation to match KiCad's coordinate system
            rotated_x, rotated_y = rotate_offset(x_offset_mm, y_offset_mm, -key.rotation)

            # Final position
            final_x_mm = base_x_mm + rotated_x
            final_y_mm = base_y_mm + rotated_y

            # Set position (convert mm to internal units)
            pos = pcbnew.VECTOR2I(mm_to_nm(final_x_mm), mm_to_nm(final_y_mm))
            fp.SetPosition(pos)

            # Set orientation (base + key rotation)
            # Negate key.rotation because KiCad uses opposite rotation direction from KDT
            total_rotation = config.orientation_deg - key.rotation
            angle = pcbnew.EDA_ANGLE(total_rotation, pcbnew.DEGREES_T)
            fp.SetOrientation(angle)

            # Set layer
            if config.pcb_side == "Bottom":
                ensure_on_back(fp)
            else:
                ensure_on_front(fp)

            return PlacementResult(
                reference=reference,
                success=True,
                message=f"Placed at ({final_x_mm:.2f}, {final_y_mm:.2f}) mm, {total_rotation}°"
            )

        except Exception as e:
            return PlacementResult(
                reference=reference,
                success=False,
                message=f"Error placing {reference}: {str(e)}"
            )

    def _categorize_result(
        self,
        result: PlacementResult,
        placed: List[PlacementResult],
        missing: List[PlacementResult],
        errors: List[PlacementResult]
    ):
        """Categorize a placement result into the appropriate list."""
        if result.success:
            placed.append(result)
        elif "not found" in result.message:
            missing.append(result)
        else:
            errors.append(result)
