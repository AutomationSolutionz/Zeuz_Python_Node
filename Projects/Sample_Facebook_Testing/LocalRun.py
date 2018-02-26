# -*- coding: utf-8 -*-
# -*- coding: cp1252 -*-
'''
@author: Automation Solutionz
'''
import sys
import os
import time

sys.path.append(os.path.dirname(os.getcwd()))
from Projects.Sample_Facebook_Testing import Facebook as facebook
from Framework.Built_In_Automation.Sequential_Actions import sequential_actions as sa


web_link_step = [ ( 'web_page' , '' , 'http://amazon.ca' , False , False , '' ) ]
dependency = {'Browser': 'chrome'}

def Launch_FB_App():
    step_data = [
        [
            ('package', 'element parameter', 'com.facebook.katana'),
            ('launch', 'appium action', 'na')
        ]
    ]
    sa.Sequential_Actions(step_data)

def Login_To_Facebook_App_Test_Case():
    Launch_FB_App()
    login_to_fb_step_data=[
        [
            ['username','','user_your_own_fb_username'],
            ['password','','user_your_own_fb_password']
        ]
    ]
    facebook.Login_to_Facebook(login_to_fb_step_data)


if __name__ == '__main__':
    Login_To_Facebook_App_Test_Case()
