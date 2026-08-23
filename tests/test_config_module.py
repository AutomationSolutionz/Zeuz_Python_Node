from Framework.Utilities import ConfigModule
from pathlib import Path
from tempfile import TemporaryDirectory


def test_local_screenshot_setting_is_not_shadowed_by_remote_config(tmp_path):
    settings = tmp_path / "settings.conf"
    settings.write_text("[Advanced Options]\ntake_screenshot = False\n")
    previous = ConfigModule.remote_config
    try:
        ConfigModule.remote_config = {"take_screenshot": True}
        assert ConfigModule.get_config_value("Advanced Options", "take_screenshot", settings) == "False"
    finally:
        ConfigModule.remote_config = previous


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        test_local_screenshot_setting_is_not_shadowed_by_remote_config(Path(directory))
