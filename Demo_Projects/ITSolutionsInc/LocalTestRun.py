'''
Created on May 16, 2016

@author: hossa
'''
from Demo_Projects.ITSolutionsInc.ITSolutionsInc import *


def Sample_test_Case_1():
    print Browser_Selection('firefox')
    print Open_Link('https://engitsolutions.sharepoint.com/sites/Demo/')
    print Login_To_Application("demo@itsolutionsinc.ca","test1234.",'cred_userid_inputtext',"cred_password_inputtext","cred_sign_in_button",logged_name=False)
    print Select_Gear_Menu_Item("Site Contents")

def Sample_test_Case_2():
    print Browser_Selection('firefox')
    print Open_Link('http://qa-factory.assetscience.com/totalanalysis/login/auth')
    print Login_To_Application("rhossain","test1234.",'username',"password","submit",logged_name=False)
    print Click_By_Parameter_And_Value('href',"/totalanalysis/devicesearch")   

href="/totalanalysis/devicesearch"    
Sample_test_Case_1()    
#Sample_test_Case_2()   