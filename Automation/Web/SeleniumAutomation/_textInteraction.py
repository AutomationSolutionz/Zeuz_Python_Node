__author__ = 'shetu'

import os
import sys
import time
from Automation.Web.SeleniumAutomation._locateInteraction import Locate_Element_By_Class,Locate_Element_By_Name
from Automation.Web.SeleniumAutomation._locateInteraction import Locate_Element_By_ID
def Set_Text_By_ID(element_name,text_value,parent=False):
    try:
        time.sleep(4)
        e=Locate_Element_By_ID(element_name,parent)
        e.clear()
        e.send_keys(text_value)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        
def Set_Text_By_Name(element_name,text_value,parent=False):
    try:
        e=Locate_Element_By_Name(element_name,parent)
        e.clear()
        e.send_keys(text_value)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))

def Set_Text_By_Class(element_name,text_value,parent=False):
    try:
        e=Locate_Element_By_Class(element_name,parent)
        e.clear()
        e.send_keys(text_value)
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
