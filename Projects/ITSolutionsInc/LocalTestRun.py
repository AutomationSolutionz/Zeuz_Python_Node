# -*- coding: cp1252 -*-
'''
Created on May 15, 2016

@author: Built_In_Automation Solutionz Inc.
'''
import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from Projects.ITSolutionsInc import ITSolutionsInc as ITS


def Delete_Sub_Site():
    result = ITS.BuiltInFunctions.Open_Browser('firefox')
    if result == "failed": return False
    result = ITS.BuiltInFunctions.Go_To_Link('https://engitsolutions.sharepoint.com/sites/Demo/')
    if result == "failed": return False
    result = ITS.BuiltInFunctions.Login_To_Application("demo@itsolutionsinc.ca","test1234.",'cred_userid_inputtext',"cred_password_inputtext","cred_sign_in_button",logged_name=False)
    if result == "failed": return False


  

def Create_Site_Content():
    ITS.BuiltInFunctions.Open_Browser('firefox')
    ITS.BuiltInFunctions.Go_To_Link('https://engitsolutions.sharepoint.com/sites/Demo/')
    ITS.BuiltInFunctions.Login_To_Application("demo@itsolutionsinc.ca","test1234.",'cred_userid_inputtext',"cred_password_inputtext","cred_sign_in_button",logged_name=False)
    ITS.Select_Gear_Menu_Item("Site contents")
    ITS.Delete_Sub_Site('Automated Sub Site')
    ITS.Select_Gear_Menu_Item("Site contents")
    ITS.Create_New_Subsite("Automated Sub Site","This description was filled out by automation","Automated_Sub_Site")




def Create_Site_Edit_Page():
    result = ITS.BuiltInFunctions.Open_Browser('firefox')
    if result == "failed": return False
    result = ITS.BuiltInFunctions.Go_To_Link('https://engitsolutions.sharepoint.com/sites/Demo/')
    if result == "failed": return False
    result = ITS.BuiltInFunctions.Login_To_Application("demo@itsolutionsinc.ca","test1234.",'cred_userid_inputtext',"cred_password_inputtext","cred_sign_in_button",logged_name=False)
    if result == "failed": return False
    result = ITS.Select_Gear_Menu_Item("Edit page")
    if result == "failed": return False



#Delete_Sub_Site() 
Create_Site_Content()    
#Sample_test_Case_2()  


