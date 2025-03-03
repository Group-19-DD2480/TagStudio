import os
from pathlib import Path
from unittest.mock import patch

import pytest
from src.core.enums import SettingItems
from src.qt.modals.settings_panel import SettingsPanel
from src.qt.widgets.preview_panel import PreviewPanel


# Tests to see if the file path setting is applied correctly
@pytest.mark.parametrize(
    "filepath_option", ["show full path", "show relative path", "show only file name"]
)
def test_filepath_setting(qtbot, qt_driver, filepath_option):
    settings_panel = SettingsPanel(qt_driver)
    qtbot.addWidget(settings_panel)

    # Mock the update_recent_lib_menu method
    with patch.object(qt_driver, "update_recent_lib_menu", return_value=None):
        # Set the file path option
        settings_panel.filepath_combobox.setCurrentText(filepath_option)
        settings_panel.apply_filepath_setting()

        # Assert the setting is applied
        assert qt_driver.settings.value(SettingItems.SHOW_FILEPATH) == filepath_option


# Tests to see if the file paths are being displayed correctly
@pytest.mark.parametrize(
    "filepath_option, expected_path",
    [
        ("show full path", lambda library: Path(library.library_dir / "one/two/bar.md")),
        ("show relative path", lambda library: Path("one/two/bar.md")),
        ("show only file name", lambda library: Path("bar.md")),
    ],
)
def test_file_path_display(qt_driver, library, filepath_option, expected_path):
    panel = PreviewPanel(library, qt_driver)

    # Select 2
    qt_driver.toggle_item_selection(2, append=False, bridge=False)
    panel.update_widgets()

    with patch.object(qt_driver.settings, "value", return_value=filepath_option):
        # Apply the mock value
        filename = library.get_entry(2).path
        panel.file_attrs.update_stats(filepath=Path(library.library_dir / filename))

        # Generate the expected file string. 
        # This is copied directly from the file_attributes.py file
        # can be imported as a function in the future
        display_path = expected_path(library)
        file_str: str = ""
        separator: str = f"<a style='color: #777777'><b>{os.path.sep}</a>"  # Gray
        for i, part in enumerate(display_path.parts):
            part_ = part.strip(os.path.sep)
            if i != len(display_path.parts) - 1:
                file_str += f"{"\u200b".join(part_)}{separator}</b>"
            else:
                if file_str != "":
                    file_str += "<br>"
                file_str += f"<b>{"\u200b".join(part_)}</b>"

        # Assert the file path is displayed correctly
        assert panel.file_attrs.file_label.text() == file_str
