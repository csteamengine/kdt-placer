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


class KDTPlacerDialog(wx.Dialog):
    """Main settings dialog for KDT Placer."""

    def __init__(self, parent):
        super().__init__(
            parent,
            title="KDT Placer - Keyboard Layout Placement",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        # Store additional component controls as list of dicts
        self.additional_components: List[dict] = []

        self._create_ui()
        self._load_saved_settings()
        self.SetSize(700, 600)
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
        main_sizer.Add(self._create_additional_components(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Buttons
        main_sizer.Add(self._create_buttons(), 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.SetSizer(main_sizer)

    def _create_main_settings(self) -> wx.StaticBoxSizer:
        """Create the main settings section."""
        box = wx.StaticBox(self, label="Main Settings")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        # JSON File row
        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_sizer.Add(wx.StaticText(self, label="JSON File:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.json_file_ctrl = wx.TextCtrl(self)
        file_sizer.Add(self.json_file_ctrl, 1, wx.EXPAND | wx.RIGHT, 5)
        browse_btn = wx.Button(self, label="Browse...", size=(80, -1))
        browse_btn.Bind(wx.EVT_BUTTON, self._on_browse)
        file_sizer.Add(browse_btn, 0)
        sizer.Add(file_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Step X, Step Y, Reference Unit in one row
        params_sizer = wx.BoxSizer(wx.HORIZONTAL)
        params_sizer.Add(wx.StaticText(self, label="Step X (mm):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.step_x_ctrl = wx.TextCtrl(self, value="19.05", size=(60, -1))
        params_sizer.Add(self.step_x_ctrl, 0, wx.RIGHT, 15)

        params_sizer.Add(wx.StaticText(self, label="Step Y (mm):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.step_y_ctrl = wx.TextCtrl(self, value="19.05", size=(60, -1))
        params_sizer.Add(self.step_y_ctrl, 0, wx.RIGHT, 15)

        ref_label = wx.StaticText(self, label="Ref Unit (px):")
        ref_label.SetToolTip("Size of 1U key in the JSON file (in pixels).\n"
                            "This is the pixel width/height of a standard 1U key\n"
                            "in your KDT layout. Default is 60px.\n\n"
                            "To find this: check the 'width' of a 1U key node in your JSON.")
        params_sizer.Add(ref_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.ref_unit_ctrl = wx.TextCtrl(self, value="60", size=(60, -1))
        self.ref_unit_ctrl.SetToolTip("Pixel size of 1U in the JSON layout")
        params_sizer.Add(self.ref_unit_ctrl, 0)

        sizer.Add(params_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Layout offset row
        offset_sizer = wx.BoxSizer(wx.HORIZONTAL)
        offset_label = wx.StaticText(self, label="Layout Offset:")
        offset_label.SetToolTip("Shift the entire layout by this amount (in mm)")
        offset_sizer.Add(offset_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        offset_sizer.Add(wx.StaticText(self, label="X:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        self.offset_x_ctrl = wx.TextCtrl(self, value="0", size=(60, -1))
        self.offset_x_ctrl.SetToolTip("X offset in mm (shifts layout right)")
        offset_sizer.Add(self.offset_x_ctrl, 0, wx.RIGHT, 15)

        offset_sizer.Add(wx.StaticText(self, label="Y:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        self.offset_y_ctrl = wx.TextCtrl(self, value="0", size=(60, -1))
        self.offset_y_ctrl.SetToolTip("Y offset in mm (shifts layout down)")
        offset_sizer.Add(self.offset_y_ctrl, 0)

        sizer.Add(offset_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        return sizer

    def _create_switch_settings(self) -> wx.StaticBoxSizer:
        """Create the switch settings section."""
        box = wx.StaticBox(self, label="Switch Footprint Settings")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        row_sizer.Add(wx.StaticText(self, label="Pattern:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.switch_pattern_ctrl = wx.TextCtrl(self, value="SW{}", size=(80, -1))
        row_sizer.Add(self.switch_pattern_ctrl, 0, wx.RIGHT, 15)

        row_sizer.Add(wx.StaticText(self, label="Rotation:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.switch_orientation_ctrl = wx.TextCtrl(self, value="0", size=(50, -1))
        row_sizer.Add(self.switch_orientation_ctrl, 0, wx.RIGHT, 15)

        row_sizer.Add(wx.StaticText(self, label="Side:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.switch_side_choice = wx.Choice(self, choices=["Top", "Bottom"])
        self.switch_side_choice.SetSelection(0)
        row_sizer.Add(self.switch_side_choice, 0)

        sizer.Add(row_sizer, 0, wx.ALL, 5)

        return sizer

    def _create_diode_settings(self) -> wx.StaticBoxSizer:
        """Create the diode settings section."""
        box = wx.StaticBox(self, label="Diode Settings")
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        row_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.diode_enabled_cb = wx.CheckBox(self, label="Enable")
        self.diode_enabled_cb.SetValue(True)
        row_sizer.Add(self.diode_enabled_cb, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 15)

        row_sizer.Add(wx.StaticText(self, label="Pattern:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.diode_pattern_ctrl = wx.TextCtrl(self, value="D{}", size=(70, -1))
        row_sizer.Add(self.diode_pattern_ctrl, 0, wx.RIGHT, 10)

        row_sizer.Add(wx.StaticText(self, label="X:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        self.diode_x_offset_ctrl = wx.TextCtrl(self, value="0", size=(40, -1))
        row_sizer.Add(self.diode_x_offset_ctrl, 0, wx.RIGHT, 10)

        row_sizer.Add(wx.StaticText(self, label="Y:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        self.diode_y_offset_ctrl = wx.TextCtrl(self, value="5", size=(40, -1))
        row_sizer.Add(self.diode_y_offset_ctrl, 0, wx.RIGHT, 10)

        row_sizer.Add(wx.StaticText(self, label="Rot:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        self.diode_orientation_ctrl = wx.TextCtrl(self, value="0", size=(40, -1))
        row_sizer.Add(self.diode_orientation_ctrl, 0, wx.RIGHT, 10)

        row_sizer.Add(wx.StaticText(self, label="Side:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.diode_side_choice = wx.Choice(self, choices=["Top", "Bottom"])
        self.diode_side_choice.SetSelection(1)  # Default to Bottom
        row_sizer.Add(self.diode_side_choice, 0)

        sizer.Add(row_sizer, 0, wx.ALL, 5)

        return sizer

    def _create_additional_components(self) -> wx.StaticBoxSizer:
        """Create the additional components section."""
        self.additional_box = wx.StaticBox(self, label="Additional Components")
        sizer = wx.StaticBoxSizer(self.additional_box, wx.VERTICAL)

        # Container for component rows
        self.additional_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.additional_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Add button
        add_btn = wx.Button(self, label="+ Add Component")
        self.Bind(wx.EVT_BUTTON, self._on_add_component, add_btn)
        sizer.Add(add_btn, 0, wx.LEFT | wx.BOTTOM, 5)

        return sizer

    def _create_component_row(self, name: str = "", pattern: str = "LED{}",
                               x_offset: str = "0", y_offset: str = "0",
                               rotation: str = "0", side: str = "Top") -> dict:
        """Create a row of controls for an additional component."""
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        controls = []  # Track all controls for cleanup

        lbl = wx.StaticText(self, label="Name:")
        controls.append(lbl)
        row_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        name_ctrl = wx.TextCtrl(self, value=name, size=(60, -1))
        controls.append(name_ctrl)
        row_sizer.Add(name_ctrl, 0, wx.RIGHT, 8)

        lbl = wx.StaticText(self, label="Pattern:")
        controls.append(lbl)
        row_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        pattern_ctrl = wx.TextCtrl(self, value=pattern, size=(70, -1))
        controls.append(pattern_ctrl)
        row_sizer.Add(pattern_ctrl, 0, wx.RIGHT, 8)

        lbl = wx.StaticText(self, label="X:")
        controls.append(lbl)
        row_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        x_ctrl = wx.TextCtrl(self, value=x_offset, size=(40, -1))
        controls.append(x_ctrl)
        row_sizer.Add(x_ctrl, 0, wx.RIGHT, 8)

        lbl = wx.StaticText(self, label="Y:")
        controls.append(lbl)
        row_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        y_ctrl = wx.TextCtrl(self, value=y_offset, size=(40, -1))
        controls.append(y_ctrl)
        row_sizer.Add(y_ctrl, 0, wx.RIGHT, 8)

        lbl = wx.StaticText(self, label="Rot:")
        controls.append(lbl)
        row_sizer.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        rot_ctrl = wx.TextCtrl(self, value=rotation, size=(40, -1))
        controls.append(rot_ctrl)
        row_sizer.Add(rot_ctrl, 0, wx.RIGHT, 8)

        side_choice = wx.Choice(self, choices=["Top", "Bottom"])
        side_choice.SetSelection(0 if side == "Top" else 1)
        controls.append(side_choice)
        row_sizer.Add(side_choice, 0, wx.RIGHT, 8)

        remove_btn = wx.Button(self, label="X", size=(25, -1))
        controls.append(remove_btn)
        row_sizer.Add(remove_btn, 0)

        component = {
            'sizer': row_sizer,
            'name': name_ctrl,
            'pattern': pattern_ctrl,
            'x_offset': x_ctrl,
            'y_offset': y_ctrl,
            'rotation': rot_ctrl,
            'side': side_choice,
            'remove_btn': remove_btn,
            'controls': controls
        }

        # Bind remove button - need to capture component dict after it's fully created
        def make_remove_handler(comp):
            def handler(event):
                self._on_remove_component(comp)
            return handler

        self.Bind(wx.EVT_BUTTON, make_remove_handler(component), remove_btn)

        return component

    def _on_add_component(self, event):
        """Add a new additional component row."""
        name = f"Comp{len(self.additional_components) + 1}"
        component = self._create_component_row(name=name)
        self.additional_components.append(component)
        self.additional_sizer.Add(component['sizer'], 0, wx.EXPAND | wx.BOTTOM, 5)
        self.Layout()
        self.Fit()

    def _on_remove_component(self, component: dict):
        """Remove an additional component row."""
        if component not in self.additional_components:
            return
        self.additional_components.remove(component)
        # Destroy all controls
        for ctrl in component['controls']:
            ctrl.Destroy()
        # Remove and clear the sizer
        self.additional_sizer.Remove(component['sizer'])
        self.Layout()
        self.Fit()

    def _create_buttons(self) -> wx.BoxSizer:
        """Create the dialog buttons."""
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        reset_btn = wx.Button(self, label="Reset Defaults")
        reset_btn.Bind(wx.EVT_BUTTON, self._on_reset_defaults)
        sizer.Add(reset_btn, 0, wx.RIGHT, 10)

        sizer.AddStretchSpacer()

        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancel")
        ok_btn = wx.Button(self, wx.ID_OK, "Place Footprints")
        ok_btn.SetDefault()

        sizer.Add(cancel_btn, 0, wx.RIGHT, 5)
        sizer.Add(ok_btn, 0)

        return sizer

    def _on_reset_defaults(self, event):
        """Reset all settings to defaults."""
        self.json_file_ctrl.SetValue("")
        self.step_x_ctrl.SetValue("19.05")
        self.step_y_ctrl.SetValue("19.05")
        self.ref_unit_ctrl.SetValue("60")
        self.offset_x_ctrl.SetValue("0")
        self.offset_y_ctrl.SetValue("0")

        self.switch_pattern_ctrl.SetValue("SW{}")
        self.switch_orientation_ctrl.SetValue("0")
        self.switch_side_choice.SetSelection(0)

        self.diode_enabled_cb.SetValue(True)
        self.diode_pattern_ctrl.SetValue("D{}")
        self.diode_x_offset_ctrl.SetValue("0")
        self.diode_y_offset_ctrl.SetValue("5")
        self.diode_orientation_ctrl.SetValue("0")
        self.diode_side_choice.SetSelection(1)

        # Remove all additional components
        for comp in self.additional_components[:]:
            self._on_remove_component(comp)

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

    def get_settings(self) -> dict:
        """Get all settings from the dialog."""
        additional_configs = []
        for comp in self.additional_components:
            additional_configs.append(ComponentConfig(
                name=comp['name'].GetValue(),
                annotation_pattern=comp['pattern'].GetValue(),
                x_offset_mm=float(comp['x_offset'].GetValue() or 0),
                y_offset_mm=float(comp['y_offset'].GetValue() or 0),
                orientation_deg=float(comp['rotation'].GetValue() or 0),
                pcb_side=comp['side'].GetStringSelection(),
                enabled=True
            ))

        return {
            'json_file': self.json_file_ctrl.GetValue(),
            'step_x_mm': float(self.step_x_ctrl.GetValue() or 19.05),
            'step_y_mm': float(self.step_y_ctrl.GetValue() or 19.05),
            'ref_unit_px': float(self.ref_unit_ctrl.GetValue() or 60),
            'offset_x_mm': float(self.offset_x_ctrl.GetValue() or 0),
            'offset_y_mm': float(self.offset_y_ctrl.GetValue() or 0),
            'switch_config': ComponentConfig(
                name="Switch",
                annotation_pattern=self.switch_pattern_ctrl.GetValue(),
                x_offset_mm=0,
                y_offset_mm=0,
                orientation_deg=float(self.switch_orientation_ctrl.GetValue() or 0),
                pcb_side=self.switch_side_choice.GetStringSelection(),
                enabled=True
            ),
            'diode_config': ComponentConfig(
                name="Diode",
                annotation_pattern=self.diode_pattern_ctrl.GetValue(),
                x_offset_mm=float(self.diode_x_offset_ctrl.GetValue() or 0),
                y_offset_mm=float(self.diode_y_offset_ctrl.GetValue() or 5),
                orientation_deg=float(self.diode_orientation_ctrl.GetValue() or 0),
                pcb_side=self.diode_side_choice.GetStringSelection(),
                enabled=self.diode_enabled_cb.GetValue()
            ),
            'additional_configs': additional_configs
        }

    def get_serializable_settings(self) -> dict:
        """Get settings in a format that can be serialized to JSON."""
        additional = []
        for comp in self.additional_components:
            additional.append({
                'name': comp['name'].GetValue(),
                'pattern': comp['pattern'].GetValue(),
                'x_offset': comp['x_offset'].GetValue(),
                'y_offset': comp['y_offset'].GetValue(),
                'orientation': comp['rotation'].GetValue(),
                'side': comp['side'].GetStringSelection()
            })

        return {
            'json_file': self.json_file_ctrl.GetValue(),
            'step_x': self.step_x_ctrl.GetValue(),
            'step_y': self.step_y_ctrl.GetValue(),
            'ref_unit': self.ref_unit_ctrl.GetValue(),
            'offset_x': self.offset_x_ctrl.GetValue(),
            'offset_y': self.offset_y_ctrl.GetValue(),
            'switch_pattern': self.switch_pattern_ctrl.GetValue(),
            'switch_orientation': self.switch_orientation_ctrl.GetValue(),
            'switch_side': self.switch_side_choice.GetSelection(),
            'diode_enabled': self.diode_enabled_cb.GetValue(),
            'diode_pattern': self.diode_pattern_ctrl.GetValue(),
            'diode_x_offset': self.diode_x_offset_ctrl.GetValue(),
            'diode_y_offset': self.diode_y_offset_ctrl.GetValue(),
            'diode_orientation': self.diode_orientation_ctrl.GetValue(),
            'diode_side': self.diode_side_choice.GetSelection(),
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

        if 'json_file' in settings:
            self.json_file_ctrl.SetValue(settings['json_file'])
        if 'step_x' in settings:
            self.step_x_ctrl.SetValue(settings['step_x'])
        if 'step_y' in settings:
            self.step_y_ctrl.SetValue(settings['step_y'])
        if 'ref_unit' in settings:
            self.ref_unit_ctrl.SetValue(settings['ref_unit'])
        if 'offset_x' in settings:
            self.offset_x_ctrl.SetValue(settings['offset_x'])
        if 'offset_y' in settings:
            self.offset_y_ctrl.SetValue(settings['offset_y'])

        if 'switch_pattern' in settings:
            self.switch_pattern_ctrl.SetValue(settings['switch_pattern'])
        if 'switch_orientation' in settings:
            self.switch_orientation_ctrl.SetValue(settings['switch_orientation'])
        if 'switch_side' in settings:
            self.switch_side_choice.SetSelection(settings['switch_side'])

        if 'diode_enabled' in settings:
            self.diode_enabled_cb.SetValue(settings['diode_enabled'])
        if 'diode_pattern' in settings:
            self.diode_pattern_ctrl.SetValue(settings['diode_pattern'])
        if 'diode_x_offset' in settings:
            self.diode_x_offset_ctrl.SetValue(settings['diode_x_offset'])
        if 'diode_y_offset' in settings:
            self.diode_y_offset_ctrl.SetValue(settings['diode_y_offset'])
        if 'diode_orientation' in settings:
            self.diode_orientation_ctrl.SetValue(settings['diode_orientation'])
        if 'diode_side' in settings:
            self.diode_side_choice.SetSelection(settings['diode_side'])

        if 'additional_components' in settings:
            for comp_data in settings['additional_components']:
                component = self._create_component_row(
                    name=comp_data.get('name', ''),
                    pattern=comp_data.get('pattern', 'LED{}'),
                    x_offset=comp_data.get('x_offset', '0'),
                    y_offset=comp_data.get('y_offset', '0'),
                    rotation=comp_data.get('orientation', '0'),
                    side=comp_data.get('side', 'Top')
                )
                self.additional_components.append(component)
                self.additional_sizer.Add(component['sizer'], 0, wx.EXPAND | wx.BOTTOM, 5)

    def validate(self) -> Tuple[bool, str]:
        """Validate the dialog settings."""
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

        for comp in self.additional_components:
            if "{}" not in comp['pattern'].GetValue():
                return False, f"Additional component '{comp['name'].GetValue()}' pattern must contain {{}}"

        return True, ""
