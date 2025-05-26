import os
from pathlib import Path

from Framework.Utilities import ConfigModule


# BASE_DIR or PROJECT_ROOT or Zeuz_Python_Node dir
PROJECT_ROOT = Path(__file__).parent

# AutomationLog dir
AutomationLog_DIR = PROJECT_ROOT / "AutomationLog"

# attachments dir
attachments_DIR = AutomationLog_DIR / "attachments"

# settings.conf file
settings_conf_dir = PROJECT_ROOT / "Framework" / "settings.conf"

# temp_ini_file = os.path.join(
#         os.path.join(
#             os.path.abspath(__file__).split("Framework")[0],
#             os.path.join(
#                 "AutomationLog",
#                 ConfigModule.get_config_value("Advanced Options", "_file"),
#             ),
#         )
#     )

# temp_config.ini file
# temp_ini_file = AutomationLog_DIR / "temp_config.ini"
# temp_ini_file = AutomationLog_DIR / ConfigModule.get_config_value("Advanced Options", "_file", settings_conf_dir)
temp_ini_file = AutomationLog_DIR / ConfigModule.get_config_value("Advanced Options", "_file")

performance_report_dir = ConfigModule.get_config_value("sectionOne", "performance_report", temp_ini_file)
