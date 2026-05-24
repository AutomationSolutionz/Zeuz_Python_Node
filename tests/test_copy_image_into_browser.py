import unittest
from unittest.mock import MagicMock, mock_open, patch

from Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions import (
    copy_image_into_browser,
)


class CopyImageIntoBrowserTests(unittest.TestCase):
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.path_parser")
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.os.access", return_value=True)
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.os.path.isfile", return_value=True)
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.os.path.exists", return_value=True)
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.open", new_callable=mock_open, read_data=b"fakepng")
    def test_accepts_single_image_file_row_with_mixed_variable_path(
        self,
        mock_open_file,
        mock_exists,
        mock_isfile,
        mock_access,
        mock_path_parser,
        mock_exec_log,
        mock_driver,
    ):
        mock_path_parser.return_value = "/resolved/image.png"
        mock_driver.capabilities = {"browserName": "chrome"}
        mock_driver.execute_cdp_cmd = MagicMock()

        result = copy_image_into_browser(
            [("image file", "input parameter", "%|var|%/whatever.png")]
        )

        self.assertEqual(result, "passed")
        mock_path_parser.assert_called_once_with("%|var|%/whatever.png")
        mock_driver.execute_cdp_cmd.assert_called_once()
        mock_exec_log.assert_any_call(
            "copy_image_into_browser : selenium", "Image copied to clipboard via CDP: /resolved/image.png", 1
        )

    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.selenium_driver")
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.path_parser")
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.os.access", return_value=True)
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.os.path.isfile", return_value=True)
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.os.path.exists", return_value=True)
    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.open", new_callable=mock_open, read_data=b"fakepng")
    def test_accepts_single_literal_image_path_row(
        self,
        mock_open_file,
        mock_exists,
        mock_isfile,
        mock_access,
        mock_path_parser,
        mock_exec_log,
        mock_driver,
    ):
        mock_path_parser.side_effect = lambda value: value
        mock_driver.capabilities = {"browserName": "chrome"}
        mock_driver.execute_cdp_cmd = MagicMock()

        result = copy_image_into_browser(
            [("image file", "input parameter", "/tmp/whatever.png")]
        )

        self.assertEqual(result, "passed")
        mock_path_parser.assert_called_once_with("/tmp/whatever.png")
        mock_driver.execute_cdp_cmd.assert_called_once()
        mock_exec_log.assert_any_call(
            "copy_image_into_browser : selenium", "Image copied to clipboard via CDP: /tmp/whatever.png", 1
        )

    @patch("Framework.Built_In_Automation.Web.Selenium.BuiltInFunctions.CommonUtil.ExecLog")
    def test_rejects_missing_image_file_value(self, mock_exec_log):
        result = copy_image_into_browser([])

        self.assertEqual(result, "zeuz_failed")
        mock_exec_log.assert_called_once()
        self.assertIn("image file", mock_exec_log.call_args.args[1])
