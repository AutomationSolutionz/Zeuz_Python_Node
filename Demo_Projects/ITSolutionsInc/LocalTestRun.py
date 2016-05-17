# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Automation Solutionz Inc.
'''
from Demo_Projects.ITSolutionsInc.ITSolutionsInc import *


def Sample_test_Case_1():
    print Browser_Selection('firefox')
    print Open_Link('https://engitsolutions.sharepoint.com/sites/Demo/')
    print Login_To_Application("demo@itsolutionsinc.ca","test1234.",'cred_userid_inputtext',"cred_password_inputtext","cred_sign_in_button",logged_name=False)
    print Select_Gear_Menu_Item("Site Contents")

def Sample_test_Case_2():
    print Browser_Selection('firefox')
  
Sample_test_Case_1()    
#Sample_test_Case_2()   