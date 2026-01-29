"""
wxPython dialog for KDT Placer settings.
"""

import wx
import os
import json
from typing import List, Optional, Tuple
from pathlib import Path

from .footprint_placer import ComponentConfig


# Settings file location
SETTINGS_DIR = Path.home() / ".config" / "kdt-placer"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"


def load_settings() -> dict:
    """Load settings from the config file."""
    if not SETTINGS_FILE.exists():
        return {}
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_settings(settings: dict):
    """Save settings to the config file."""
    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except IOError:
        pass  # Silently fail if we can't save


class AdditionalComponentPanel(wx.Panel):
    """Panel for configuring a single additional component."""

    def __init__(self, parent, name: str = "", on_remove=None):
        super().__init__(parent)
        self.on_remove = on_remove

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Name
        sizer.Add(wx.StaticText(self, label="Name:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.name_ctrl = wx.TextCtrl(self, value=name, size=(60, -1))
        sizer.Add(self.name_ctrl, 0, wx.RIGHT, 10)

        # Pattern
        sizer.Add(wx.StaticText(self, label="Pattern:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.pattern_ctrl = wx.TextCtrl(self, value="LED{}", size=(60, -1))
        sizer.Add(self.pattern_ctrl, 0, wx.RIGHT, 10)

        # X Offset
        sizer.Add(wx.StaticText(self, label="X:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.x_offset_ctrl = wx.TextCtrl(self, value="0", size=(45, -1))
        sizer.Add(self.x_offset_ctrl, 0, wx.RIGHT, 10)

        # Y Offset
        sizer.Add(wx.StaticText(self, label="Y:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.y_offset_ctrl = wx.TextCtrl(self, value="0", size=(45, -1))
        sizer.Add(self.y_offset_ctrl, 0, wx.RIGHT, 10)

        # Orientation
        sizer.Add(wx.StaticText(self, label="Rot:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.orientation_ctrl = wx.TextCtrl(self, value="0", size=(45, -1))
        sizer.Add(self.orientation_ctrl, 0, wx.RIGHT, 10)

        # Side
        self.side_choice = wx.Choice(self, choices=["Top", "Bottom"])
        self.side_choice.SetSelection(0)
        sizer.Add(self.side_choice, 0, wx.RIGHT, 10)

        # Remove button
        remove_btn = wx.Button(self, label="Remove", size=(60, -1))
        remove_btn.Bind(wx.EVT_BUTTON, self._on_remove)
        sizer.Add(remove_btn, 0)

        self.SetSizer(sizer)

    def _on_remove(self, event):
        if self.on_remove:
            self.on_remove(self)

    def get_config(self) -> ComponentConfig:
        """Get the component configuration from this panel."""
        return ComponentConfig(
            name=self.name_ctrl.GetValue(),
            annotation_pattern=self.pattern_ctrl.GetValue(),
            x_offset_mm=float(self.x_offset_ctrl.GetValue() or 0),
            y_offset_mm=float(self.y_offset_ctrl.GetValue() or 0),
            orientation_deg=float(self.orientation_ctrl.GetValue() or 0),
            pcb_side=self.side_choice.GetStringSelection(),
            enabled=True
        )


class KDTPlacerDialog(wx.Dialog):
    """Main settings dialog for KDT Placer."""

    def __init__(self, parent):
        super().__init__(
            parent,
            title="KDT Placer - Keyboard Layout Placement",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        self.additional_panels: List[AdditionalComponentPanel] = []

        self._create_ui()
        self._load_saved_settings()
        self.SetSize(550, 650)
        self.Centre()

    def _create_ui(self):
        """Create the dialog UI."""
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Main settings section
        main_sizer.Add(self._create_main_settings(), 0, wx.EXPAND | wx.ALL, 10)

        # Switch settings section
        main_sizer.Add(self._create_switch_settings(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Diode settings section
        main_sizer.Add(self._create_diode_settings(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Additional components section
        main_sizer.Add(self._create_additional_components(), 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Buttons
        main_sizer.Add(self._create_buttons(), 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.SetSizer(main_sizer)

    def _create_main_settings(self) -> wx.StaticBoxSizer:
        """Create the main settings section."""
        box = wx.StaticBox(self, label="Main Settings")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        grid = wx.FlexGridSizer(4, 2, 5, 10)
        grid.AddGrowableCol(1, 1)

        # JSON File
        grid.Add(wx.StaticText(self, label="JSON File:"), 0, wx.ALIGN_CENTER_VERTICAL)
        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.json_file_ctrl = wx.TextCtrl(self)
        file_sizer.Add(self.json_file_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        browse_btn = wx.Button(self, label="Browse...", size=(80, -1))
        browse_btn.Bind(wx.EVT_BUTTON, self._on_browse)
        file_sizer.Add(browse_btn, 0)
        grid.Add(file_sizer, 1, wx.EXPAND)

        # Step X
        grid.Add(wx.StaticText(self, label="Step X (mm):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.step_x_ctrl = wx.TextCtrl(self, value="19.05")
        grid.Add(self.step_x_ctrl, 1, wx.EXPAND)

        # Step Y
        grid.Add(wx.StaticText(self, label="Step Y (mm):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.step_y_ctrl = wx.TextCtrl(self, value="19.05")
        grid.Add(self.step_y_ctrl, 1, wx.EXPAND)

        # Reference Unit Size
        grid.Add(wx.StaticText(self, label="Reference Unit Size (px):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.ref_unit_ctrl = wx.TextCtrl(self, value="60")
        grid.Add(self.ref_unit_ctrl, 1, wx.EXPAND)

        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 5)
        return sizer

    def _create_switch_settings(self) -> wx.StaticBoxSizer:
        """Create the switch settings section."""
        box = wx.StaticBox(self, label="Switch Footprint Settings")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        grid = wx.FlexGridSizer(3, 2, 5, 10)
        grid.AddGrowableCol(1, 1)

        # Annotation Pattern
        grid.Add(wx.StaticText(self, label="Annotation Pattern:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.switch_pattern_ctrl = wx.TextCtrl(self, value="SW{}")
        grid.Add(self.switch_pattern_ctrl, 1, wx.EXPAND)

        # Orientation
        grid.Add(wx.StaticText(self, label="Orientation (deg):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.switch_orientation_ctrl = wx.TextCtrl(self, value="0")
        grid.Add(self.switch_orientation_ctrl, 1, wx.EXPAND)

        # PCB Side
        grid.Add(wx.StaticText(self, label="PCB Side:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.switch_side_radio = wx.RadioBox(
            self, choices=["Top", "Bottom"], style=wx.RA_HORIZONTAL
        )
        grid.Add(self.switch_side_radio, 1, wx.EXPAND)

        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 5)
        return sizer

    def _create_diode_settings(self) -> wx.StaticBoxSizer:
        """Create the diode settings section."""
        box = wx.StaticBox(self, label="Diode Settings")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        # Enabled checkbox
        self.diode_enabled_cb = wx.CheckBox(self, label="Place diodes")
        self.diode_enabled_cb.SetValue(True)
        self.diode_enabled_cb.Bind(wx.EVT_CHECKBOX, self._on_diode_enabled_change)
        sizer.Add(self.diode_enabled_cb, 0, wx.ALL, 5)

        # Settings grid
        self.diode_panel = wx.Panel(self)
        grid = wx.FlexGridSizer(5, 2, 5, 10)
        grid.AddGrowableCol(1, 1)

        # Annotation Pattern
        grid.Add(wx.StaticText(self.diode_panel, label="Annotation Pattern:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.diode_pattern_ctrl = wx.TextCtrl(self.diode_panel, value="D{}")
        grid.Add(self.diode_pattern_ctrl, 1, wx.EXPAND)

        # X Offset
        grid.Add(wx.StaticText(self.diode_panel, label="X Offset (mm):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.diode_x_offset_ctrl = wx.TextCtrl(self.diode_panel, value="0")
        grid.Add(self.diode_x_offset_ctrl, 1, wx.EXPAND)

        # Y Offset
        grid.Add(wx.StaticText(self.diode_panel, label="Y Offset (mm):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.diode_y_offset_ctrl = wx.TextCtrl(self.diode_panel, value="5")
        grid.Add(self.diode_y_offset_ctrl, 1, wx.EXPAND)

        # Orientation
        grid.Add(wx.StaticText(self.diode_panel, label="Orientation (deg):"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.diode_orientation_ctrl = wx.TextCtrl(self.diode_panel, value="0")
        grid.Add(self.diode_orientation_ctrl, 1, wx.EXPAND)

        # PCB Side
        grid.Add(wx.StaticText(self.diode_panel, label="PCB Side:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.diode_side_radio = wx.RadioBox(
            self.diode_panel, choices=["Top", "Bottom"], style=wx.RA_HORIZONTAL
        )
        self.diode_side_radio.SetSelection(1)  # Default to Bottom
        grid.Add(self.diode_side_radio, 1, wx.EXPAND)

        self.diode_panel.SetSizer(grid)
        sizer.Add(self.diode_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        return sizer

    def _create_additional_components(self) -> wx.StaticBoxSizer:
        """Create the additional components section."""
        box = wx.StaticBox(self, label="Additional Components")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        # Add button
        add_btn = wx.Button(self, label="Add Component")
        add_btn.Bind(wx.EVT_BUTTON, self._on_add_component)
        sizer.Add(add_btn, 0, wx.ALL, 5)

        # Scrolled panel for components
        self.additional_scroll = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.additional_scroll.SetScrollRate(0, 20)
        self.additional_sizer = wx.BoxSizer(wx.VERTICAL)
        self.additional_scroll.SetSizer(self.additional_sizer)

        sizer.Add(self.additional_scroll, 1, wx.EXPAND | wx.ALL, 5)

        return sizer

    def _create_buttons(self) -> wx.BoxSizer:
        """Create the dialog buttons."""
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        ok_btn = wx.Button(self, wx.ID_OK, "Place Footprints")
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancel")

        sizer.Add(ok_btn, 0, wx.RIGHT, 5)
        sizer.Add(cancel_btn, 0)

        return sizer

    def _on_browse(self, event):
        """Handle browse button click."""
        with wx.FileDialog(
            self,
            "Select KDT JSON File",
            wildcard="JSON files (*.json)|*.json|All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.json_file_ctrl.SetValue(dialog.GetPath())

    def _on_diode_enabled_change(self, event):
        """Handle diode enabled checkbox change."""
        self.diode_panel.Enable(self.diode_enabled_cb.GetValue())

    def _on_add_component(self, event):
        """Add a new additional component panel."""
        panel = AdditionalComponentPanel(
            self.additional_scroll,
            name=f"Comp{len(self.additional_panels) + 1}",
            on_remove=self._on_remove_component
        )
        self.additional_panels.append(panel)
        self.additional_sizer.Add(panel, 0, wx.EXPAND | wx.BOTTOM, 5)
        self.additional_scroll.FitInside()
        self.Layout()

    def _on_remove_component(self, panel: AdditionalComponentPanel):
        """Remove an additional component panel."""
        self.additional_panels.remove(panel)
        panel.Destroy()
        self.additional_scroll.FitInside()
        self.Layout()

    def get_settings(self) -> dict:
        """
        Get all settings from the dialog.

        Returns:
            Dictionary with all settings
        """
        return {
            'json_file': self.json_file_ctrl.GetValue(),
            'step_x_mm': float(self.step_x_ctrl.GetValue() or 19.05),
            'step_y_mm': float(self.step_y_ctrl.GetValue() or 19.05),
            'ref_unit_px': float(self.ref_unit_ctrl.GetValue() or 60),
            'switch_config': ComponentConfig(
                name="Switch",
                annotation_pattern=self.switch_pattern_ctrl.GetValue(),
                x_offset_mm=0,
                y_offset_mm=0,
                orientation_deg=float(self.switch_orientation_ctrl.GetValue() or 0),
                pcb_side=self.switch_side_radio.GetStringSelection(),
                enabled=True
            ),
            'diode_config': ComponentConfig(
                name="Diode",
                annotation_pattern=self.diode_pattern_ctrl.GetValue(),
                x_offset_mm=float(self.diode_x_offset_ctrl.GetValue() or 0),
                y_offset_mm=float(self.diode_y_offset_ctrl.GetValue() or 5),
                orientation_deg=float(self.diode_orientation_ctrl.GetValue() or 0),
                pcb_side=self.diode_side_radio.GetStringSelection(),
                enabled=self.diode_enabled_cb.GetValue()
            ),
            'additional_configs': [p.get_config() for p in self.additional_panels]
        }

    def get_serializable_settings(self) -> dict:
        """
        Get settings in a format that can be serialized to JSON.

        Returns:
            Dictionary with serializable settings
        """
        additional = []
        for panel in self.additional_panels:
            additional.append({
                'name': panel.name_ctrl.GetValue(),
                'pattern': panel.pattern_ctrl.GetValue(),
                'x_offset': panel.x_offset_ctrl.GetValue(),
                'y_offset': panel.y_offset_ctrl.GetValue(),
                'orientation': panel.orientation_ctrl.GetValue(),
                'side': panel.side_choice.GetStringSelection()
            })

        return {
            'json_file': self.json_file_ctrl.GetValue(),
            'step_x': self.step_x_ctrl.GetValue(),
            'step_y': self.step_y_ctrl.GetValue(),
            'ref_unit': self.ref_unit_ctrl.GetValue(),
            'switch_pattern': self.switch_pattern_ctrl.GetValue(),
            'switch_orientation': self.switch_orientation_ctrl.GetValue(),
            'switch_side': self.switch_side_radio.GetSelection(),
            'diode_enabled': self.diode_enabled_cb.GetValue(),
            'diode_pattern': self.diode_pattern_ctrl.GetValue(),
            'diode_x_offset': self.diode_x_offset_ctrl.GetValue(),
            'diode_y_offset': self.diode_y_offset_ctrl.GetValue(),
            'diode_orientation': self.diode_orientation_ctrl.GetValue(),
            'diode_side': self.diode_side_radio.GetSelection(),
            'additional_components': additional
        }

    def save_current_settings(self):
        """Save current dialog settings to the config file."""
        save_settings(self.get_serializable_settings())

    def _load_saved_settings(self):
        """Load and apply saved settings to the dialog controls."""
        settings = load_settings()
        if not settings:
            return

        # Main settings
        if 'json_file' in settings:
            self.json_file_ctrl.SetValue(settings['json_file'])
        if 'step_x' in settings:
            self.step_x_ctrl.SetValue(settings['step_x'])
        if 'step_y' in settings:
            self.step_y_ctrl.SetValue(settings['step_y'])
        if 'ref_unit' in settings:
            self.ref_unit_ctrl.SetValue(settings['ref_unit'])

        # Switch settings
        if 'switch_pattern' in settings:
            self.switch_pattern_ctrl.SetValue(settings['switch_pattern'])
        if 'switch_orientation' in settings:
            self.switch_orientation_ctrl.SetValue(settings['switch_orientation'])
        if 'switch_side' in settings:
            self.switch_side_radio.SetSelection(settings['switch_side'])

        # Diode settings
        if 'diode_enabled' in settings:
            self.diode_enabled_cb.SetValue(settings['diode_enabled'])
            self.diode_panel.Enable(settings['diode_enabled'])
        if 'diode_pattern' in settings:
            self.diode_pattern_ctrl.SetValue(settings['diode_pattern'])
        if 'diode_x_offset' in settings:
            self.diode_x_offset_ctrl.SetValue(settings['diode_x_offset'])
        if 'diode_y_offset' in settings:
            self.diode_y_offset_ctrl.SetValue(settings['diode_y_offset'])
        if 'diode_orientation' in settings:
            self.diode_orientation_ctrl.SetValue(settings['diode_orientation'])
        if 'diode_side' in settings:
            self.diode_side_radio.SetSelection(settings['diode_side'])

        # Additional components
        if 'additional_components' in settings:
            for comp in settings['additional_components']:
                panel = AdditionalComponentPanel(
                    self.additional_scroll,
                    name=comp.get('name', ''),
                    on_remove=self._on_remove_component
                )
                panel.pattern_ctrl.SetValue(comp.get('pattern', 'LED{}'))
                panel.x_offset_ctrl.SetValue(comp.get('x_offset', '0'))
                panel.y_offset_ctrl.SetValue(comp.get('y_offset', '0'))
                panel.orientation_ctrl.SetValue(comp.get('orientation', '0'))
                side = comp.get('side', 'Top')
                panel.side_choice.SetSelection(0 if side == 'Top' else 1)
                self.additional_panels.append(panel)
                self.additional_sizer.Add(panel, 0, wx.EXPAND | wx.BOTTOM, 5)
            self.additional_scroll.FitInside()

    def validate(self) -> Tuple[bool, str]:
        """
        Validate the dialog settings.

        Returns:
            Tuple of (is_valid, error_message)
        """
        json_file = self.json_file_ctrl.GetValue()
        if not json_file:
            return False, "Please select a JSON file"
        if not os.path.exists(json_file):
            return False, f"JSON file not found: {json_file}"

        try:
            float(self.step_x_ctrl.GetValue())
        except ValueError:
            return False, "Step X must be a number"

        try:
            float(self.step_y_ctrl.GetValue())
        except ValueError:
            return False, "Step Y must be a number"

        try:
            float(self.ref_unit_ctrl.GetValue())
        except ValueError:
            return False, "Reference Unit Size must be a number"

        if "{}" not in self.switch_pattern_ctrl.GetValue():
            return False, "Switch annotation pattern must contain {}"

        if self.diode_enabled_cb.GetValue():
            if "{}" not in self.diode_pattern_ctrl.GetValue():
                return False, "Diode annotation pattern must contain {}"

        for panel in self.additional_panels:
            if "{}" not in panel.pattern_ctrl.GetValue():
                return False, f"Additional component '{panel.name_ctrl.GetValue()}' pattern must contain {{}}"

        return True, ""
