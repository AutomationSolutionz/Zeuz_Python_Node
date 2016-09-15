'''
Created on July 4, 2016

@author: Riasat Rakin
'''

import sys
import os
sys.path.append("..")
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
import inspect
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
#Ver1.0
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from Utilities import CommonUtil
from selenium.webdriver.support import expected_conditions as EC

#Built in function import 
from Built_In_Automation.Web.SeleniumAutomation import BuiltInFunctions
from datetime import datetime


global WebDriver_Wait 
WebDriver_Wait = 20
global WebDriver_Wait_Short
WebDriver_Wait_Short = 10

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = True
#local_run = False



def Item_Search(search_text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying locate search menu", 1,local_run)
        result= BuiltInFunctions.Get_Double_Matching_Elements('aria-label', 'Search', 'placeholder', 'Search')
#        Get_Element_With_Reference('aria-label',item_text,'ispopup', '1',"parent")
        if result != "failed":
            result.click()
            CommonUtil.ExecLog(sModuleInfo, "Clicked your element", 1,local_run)            
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Failed to clicked your element", 3,local_run)            
            return "failed"
        
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not locate search bar menu item: %s.  Error: %s"%(search_text, Error_Detail), 3,local_run)
        return "failed"

