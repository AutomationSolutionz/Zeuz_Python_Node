# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''
import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from Projects.ITSolutionsInc.ITSolutionsInc import *


def Sample_test_Case_1():
    print BuiltInFunctions.Open_Browser('firefox')
    print BuiltInFunctions.Go_To_Link('https://engitsolutions.sharepoint.com/sites/Demo/')
    print BuiltInFunctions.Login_To_Application("demo@itsolutionsinc.ca","test1234.",'cred_userid_inputtext',"cred_password_inputtext","cred_sign_in_button",logged_name=False)
    print Select_Gear_Menu_Item("Site Contents")
    print Create_New_Subsite("Automated Sub Site","This description was filled out by automation","Automated_Sub_Site")

def Sample_test_Case_2():
    print BuiltInFunctions.Browser_Selection('firefox')
  
Sample_test_Case_1()    
#Sample_test_Case_2()  


