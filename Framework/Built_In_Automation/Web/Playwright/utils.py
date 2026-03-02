# -*- coding: utf-8 -*-
"""
Playwright Utility Functions for Zeuz Node

This module provides utility functions for Playwright automation,
including browser download and setup functionality.

Author: Zeuz/AutomationSolutionz
"""

import os
from pathlib import Path
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Web.Selenium.utils import ChromeForTesting

# Initialize Chrome for Testing instance
chrome_for_testing = ChromeForTesting()


def ensure_chromium_downloads(sModuleInfo):
    """
    Ensure Chrome for Testing is available for Playwright.
    
    Args:
        sModuleInfo: Module information for logging
        
    Returns:
        tuple: (chrome_binary_path, success_flag) where success_flag is True if successful
    """
    try:
        CommonUtil.ExecLog(sModuleInfo, "Setting up Chrome for Testing for Playwright...", 1)
        
        # Use Chrome for Testing to get Chrome binary
        chrome_bin, driver_bin = chrome_for_testing.setup_chrome_for_testing()
        
        if chrome_bin and chrome_bin.exists():
            CommonUtil.ExecLog(sModuleInfo, f"Chrome for Testing ready: {chrome_bin}", 1)
            return str(chrome_bin), True
        else:
            CommonUtil.ExecLog(sModuleInfo, "Failed to setup Chrome for Testing", 3)
            return None, False
            
    except Exception as e:
        CommonUtil.ExecLog(sModuleInfo, f"Error setting up Chrome for Testing: {str(e)}", 3)
        return None, False
