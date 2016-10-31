'''
Created on October 31, 2016

@author: Riasat Rakin
'''
import sys
import os
import time


from Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions
from Utilities import muxboard
from Utilities.muxboard import ConnectDisconnectDevice
from appium import webdriver

def Connect_To_MuxBoard():
    ConnectDisconnectDevice(0,2,'m')
    
Connect_To_MuxBoard()


#bf.launch_and_start_driver('com.bunz', 'com.bunz.activity.LaunchActivity')
#bf.Sequential_Actions([[[u'resource-id', u'', u'com.bunz:id/btn_login', False, False], [u'click', u'action', u'click', False, False]], [[u'resource-id', u'', u'com.bunz:id/btn_login_email', False, False], [u'click', u'action', u'click', False, False]], [[u'wait', u'action', u'5', False, False], [u'wait', u'and', u'see', False, False]], [[u'resource-id', u'', u'com.bunz:id/edt_email', False, False], [u'click', u'action', u'click', False, False]], [[u'wait', u'action', u'5', False, False], [u'wait', u'and', u'see', False, False]], [[u'resource-id', u'', u'com.bunz:id/edt_email', False, False], [u'text', u'action', u'test@bunz.com', False, False]], [[u'resource-id', u'', u'com.bunz:id/edt_password', False, False], [u'click', u'action', u'click', False, False]], [[u'wait', u'action', u'5', False, False], [u'wait', u'and', u'see', False, False]], [[u'resource-id', u'', u'com.bunz:id/edt_password', False, False], [u'text', u'action', u'password', False, False]], [[u'resource-id', u'', u'com.bunz:id/btn_login_email', False, False], [u'click', u'action', u'click', False, False]]])

#bf.Sequential_Actions([[['wait','action',float('5')],[]], [['swipe','action','swipe'],[]], [['tap','action','tap'], ['id','','com.bunz:id/fab_create_post']]])
#bf.close()