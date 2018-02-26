# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''

@author: Automation Solutionz
'''

import sys
import os
import xlrd

sys.path.append("..")
import inspect
import time
from Framework.Utilities import CommonUtil
from Framework.Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions




def Login_to_Facebook(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        no_login_to_another_account = False
        username = ""
        password = ""
        for row in step_data[0]:
            if str(row[0]).strip().lower() == 'username':
                username = str(row[2]).strip()
            elif str(row[0]).strip().lower() == 'password':
                password = str(row[2]).strip()

        time.sleep(15) #wait the fb app to load

        CommonUtil.ExecLog(sModuleInfo,'Searching for Log into Another Account Button',1)
        log_into_another_account_step_data =[
                ['text','element parameter','LOG INTO ANOTHER ACCOUNT']
            ]
        log_into_another_account_button = BuiltInFunctions.LocateElement.Get_Element(log_into_another_account_step_data,BuiltInFunctions.appium_driver)


        if log_into_another_account_button != "failed":
            CommonUtil.ExecLog(sModuleInfo, 'Found Log into Another Account Button', 1)
            CommonUtil.ExecLog(sModuleInfo, 'Trying to Click Log into Another Account Button', 1)
            BuiltInFunctions.Click_Element_Appium(log_into_another_account_step_data)
            CommonUtil.ExecLog(sModuleInfo, 'Clicked Log into Another Account Button', 1)
        else:
            no_login_to_another_account = True
            CommonUtil.ExecLog(sModuleInfo, 'Could not find Log into Another Account Button', 1)

        CommonUtil.ExecLog(sModuleInfo, 'Searching for Email text Field', 1)
        email_text_field_step_data = [
            ['class', 'element parameter', 'android.widget.EditText'],
            ['index', 'element parameter', '0'],
            ['text','action',username]
        ]

        password_text_field_step_data = [
            ['class', 'element parameter', 'android.widget.EditText'],
            ['index', 'element parameter', '1'],
            ['text', 'action', password]
        ]

        enter_key_press = [
            ['keypress','appium action','enter']
        ]

        email_text_field = BuiltInFunctions.LocateElement.Get_Element(email_text_field_step_data,BuiltInFunctions.appium_driver)

        if email_text_field != "failed":
            CommonUtil.ExecLog(sModuleInfo, 'Found Email Text Field', 1)
            CommonUtil.ExecLog(sModuleInfo, 'Trying to Enter Login Credentials', 1)
            BuiltInFunctions.Enter_Text_Appium(email_text_field_step_data)
            BuiltInFunctions.Enter_Text_Appium(password_text_field_step_data)
            CommonUtil.ExecLog(sModuleInfo, 'Entered Login Credentials', 1)
            CommonUtil.ExecLog(sModuleInfo,"Pressing ENTER button",1)
            BuiltInFunctions.Keystroke_Appium(enter_key_press)
            CommonUtil.ExecLog(sModuleInfo, "Pressed ENTER button", 1)
            time.sleep(30) # fb app login time
            CommonUtil.ExecLog(sModuleInfo, 'Tried to Perform Login Activity Successfully', 1)
            return "passed"
        else:
            if no_login_to_another_account: #user is logged in FB
                return "passed"
            else:
                CommonUtil.ExecLog(sModuleInfo, 'Could not find Email/Password Field', 1)
                return "failed"



    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(
            exc_obj) + ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo,"Could not log in to facebook app", 3)
        return "failed"