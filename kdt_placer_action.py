"""
KiCad ActionPlugin for KDT Placer.
Entry point for the plugin that connects the dialog to the placement logic.
"""

import os
import pcbnew
import wx

from .kdt_placer_dialog import KDTPlacerDialog
from .json_parser import parse_kdt_json, validate_json_structure
from .footprint_placer import FootprintPlacer, PlacementSummary


class KDTPlacerAction(pcbnew.ActionPlugin):
    """KiCad Action Plugin for placing keyboard switch footprints."""

    def defaults(self):
        """Set plugin defaults."""
        self.name = "KDT Placer"
        self.category = "Modify PCB"
        self.description = "Place keyboard switch footprints from KDT JSON layout"
        self.show_toolbar_button = True

        # Icon path (optional)
        icon_path = os.path.join(os.path.dirname(__file__), "kdt_placer.png")
        if os.path.exists(icon_path):
            self.icon_file_name = icon_path

    def Run(self):
        """Execute the plugin."""
        board = pcbnew.GetBoard()
        if board is None:
            wx.MessageBox(
                "No board is currently open.",
                "KDT Placer Error",
                wx.OK | wx.ICON_ERROR
            )
            return

        # Show dialog
        dialog = KDTPlacerDialog(None)
        result = dialog.ShowModal()

        # Always save settings when dialog closes
        dialog.save_current_settings()

        if result == wx.ID_OK:
            # Validate settings
            is_valid, error_msg = dialog.validate()
            if not is_valid:
                wx.MessageBox(
                    error_msg,
                    "KDT Placer - Validation Error",
                    wx.OK | wx.ICON_ERROR
                )
                dialog.Destroy()
                return

            settings = dialog.get_settings()

            # Validate JSON
            json_valid, json_msg = validate_json_structure(settings['json_file'])
            if not json_valid:
                wx.MessageBox(
                    f"Invalid JSON file:\n{json_msg}",
                    "KDT Placer - JSON Error",
                    wx.OK | wx.ICON_ERROR
                )
                dialog.Destroy()
                return

            # Parse JSON
            try:
                keys = parse_kdt_json(settings['json_file'])
            except Exception as e:
                wx.MessageBox(
                    f"Error parsing JSON:\n{str(e)}",
                    "KDT Placer - Parse Error",
                    wx.OK | wx.ICON_ERROR
                )
                dialog.Destroy()
                return

            # Place footprints
            placer = FootprintPlacer(board)

            diode_config = settings['diode_config'] if settings['diode_config'].enabled else None

            summary = placer.place_keys(
                keys=keys,
                switch_config=settings['switch_config'],
                diode_config=diode_config,
                additional_configs=settings['additional_configs'],
                step_x_mm=settings['step_x_mm'],
                step_y_mm=settings['step_y_mm'],
                ref_unit_px=settings['ref_unit_px']
            )

            # Refresh the board view
            pcbnew.Refresh()

            # Show summary
            self._show_summary(summary)

        dialog.Destroy()

    def _show_summary(self, summary: PlacementSummary):
        """Show a summary dialog of the placement results."""
        placed_count = len(summary.placed)
        missing_count = len(summary.missing)
        error_count = len(summary.errors)

        msg_lines = [
            f"Placement complete for {summary.total_keys} keys.",
            "",
            f"Successfully placed: {placed_count}",
            f"Missing footprints: {missing_count}",
            f"Errors: {error_count}"
        ]

        if missing_count > 0:
            msg_lines.append("")
            msg_lines.append("Missing footprints:")
            for result in summary.missing[:10]:  # Show first 10
                msg_lines.append(f"  - {result.reference}")
            if missing_count > 10:
                msg_lines.append(f"  ... and {missing_count - 10} more")

        if error_count > 0:
            msg_lines.append("")
            msg_lines.append("Errors:")
            for result in summary.errors[:5]:  # Show first 5
                msg_lines.append(f"  - {result.message}")
            if error_count > 5:
                msg_lines.append(f"  ... and {error_count - 5} more")

        icon = wx.ICON_INFORMATION if error_count == 0 else wx.ICON_WARNING

        wx.MessageBox(
            "\n".join(msg_lines),
            "KDT Placer - Summary",
            wx.OK | icon
        )
