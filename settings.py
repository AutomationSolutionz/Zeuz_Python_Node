import os
from pathlib import Path

from Framework.Utilities import ConfigModule


# BASE_DIR or PROJECT_ROOT
PROJECT_ROOT = Path(__file__).parent

# AutomationLog directory
AutomationLog_DIR = PROJECT_ROOT / "AutomationLog"

# temp_ini_file = os.path.join(
#         os.path.join(
#             os.path.abspath(__file__).split("Framework")[0],
#             os.path.join(
#                 "AutomationLog",
#                 ConfigModule.get_config_value("Advanced Options", "_file"),
#             ),
#         )
#     )

temp_ini_file = AutomationLog_DIR / ConfigModule.get_config_value("Advanced Options", "_file")

performance_report_dir = ConfigModule.get_config_value("sectionOne", "performance_report", temp_ini_file)
