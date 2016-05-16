'''
Created on May 16, 2016

@author: hossa
'''
from Demo_Projects.ITSolutionsInc.ITSolutionsInc import *

def Sample_test_Case_1():
    print BrowserSelection('firefox')
    print OpenLink('https://engitsolutions.sharepoint.com/sites/Demo/')
    print Login_To_Application("demo@itsolutionsinc.ca","test1234.",'cred_userid_inputtext',"cred_password_inputtext","cred_sign_in_button",logged_name=False)
    print Click_By_Parameter_And_Value('title',"Open the Settings menu to access personal and app settings", parent=False)
    print Click_By_Parameter_And_Value('aria-label',"Site contents", parent=False)
    print Click_By_Parameter_And_Value('alt',"new subsite", parent=False) 

def Sample_test_Case_2():
    print BrowserSelection('firefox')
    print OpenLink('http://qa-factory.assetscience.com/totalanalysis/login/auth')
    print Login_To_Application("rhossain","test1234.",'username',"password","submit",logged_name=False)
    print Click_By_Parameter_And_Value('href',"/totalanalysis/devicesearch")   

href="/totalanalysis/devicesearch"    
#Sample_test_Case_1()    
Sample_test_Case_2()   