# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Automation Solutionz Inc.
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
from Automation.Web.SeleniumAutomation import BuiltInFunctions


global WebDriver_Wait 
WebDriver_Wait = 20
global WebDriver_Wait_Short
WebDriver_Wait_Short = 10

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
local_run = True
#local_run = False

  

def Select_Gear_Menu_Item(item_text):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo, "Trying to click on Settings Gear Icon", 1,local_run)
        try:
            BuiltInFunctions.Click_By_Parameter_And_Value('title',"Open the Settings menu to access personal and app settings", parent=False)
        except:
            CommonUtil.ExecLog(sModuleInfo, "Could not click on the Gear icon", 3,local_run)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            return "failed"  
        #We now look for the pop up menu 
        CommonUtil.ExecLog(sModuleInfo, "Trying locate the pop up window menu", 1,local_run)
        try:
            pop_up_menu = BuiltInFunctions.Get_Element("ispopup","1")
        except:
            CommonUtil.ExecLog(sModuleInfo, "Could not locate pop up menu", 3,local_run)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            return "failed"  
        if pop_up_menu == "failed":
            CommonUtil.ExecLog(sModuleInfo, "Could not locate pop up menu", 3,local_run)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            return "failed"  
        #Now that we have located the pop up menu, we can click on any item in that menu
        result = BuiltInFunctions.Click_Element_By_Name(item_text,pop_up_menu) 
        if result == "passed":   
            CommonUtil.ExecLog(sModuleInfo, "Successfully clicked your Gear menu item %s"%item_text, 1,local_run)        
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Could not click on the Gear menu item: %s"%item_text, 3,local_run)
            CommonUtil.TakeScreenShot(sModuleInfo, local_run)
            return "failed"                
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Could not click on the Gear menu item: %s.  Error: %s"%(item_text, Error_Detail), 3,local_run)
        return "failed"       
    
