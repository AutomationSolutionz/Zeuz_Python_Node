__author__ = 'shetu'
import sys
import os
import inspect
from selenium import webdriver
from Built_In_Automation.Web.SeleniumAutomation import BuiltInFunctions as config
from Built_In_Automation.Web.SeleniumAutomation._locateInteraction import Locate_Element_By_Tag
from Built_In_Automation.Web.SeleniumAutomation import _textInteraction as t
from Built_In_Automation.Web.SeleniumAutomation import _clickInteraction as c
from Utilities import CommonUtil

#Get the initiated global driver
sBrowser = config.get_driver()
global sBrowser


def dataRetrieval(tag_name,index_list,parent=False):
    try:
        if index_list:
            element_list=Locate_Element_By_Tag(tag_name,parent,True)
        else:
            element_list=Locate_Element_By_Tag(tag_name,parent)
        if index_list:
            t=[]
            for i in element_list:
                #needs to be changed
                child=i.find_elements_by_xpath('.//*')
                m=[]
                for each in index_list:
                    m.append(child[each-1].text)
                t.append(tuple(m))
            return t
        else:
            return element_list.text
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        
        