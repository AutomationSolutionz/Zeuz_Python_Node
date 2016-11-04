'''
Created on October 31, 2016

@author: Riasat Rakin
'''
import sys
import os
import time


from Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf
from Utilities import muxboard
from Utilities.muxboard import ConnectDisconnectDevice
from appium import webdriver
from time import sleep


def Get_Port_To_Connect(port_number):
    number = port_number.split(',')
    return number

def ConnectedDeviceAction():
    bf.launch('com.google.android.youtube', 'com.google.android.youtube.HomeActivity')
    #sleep(3)
    bf.Keystroke_Appium([ [ ( 'Android keystroke' , 'action' , 'go back' , False , False ) ] ] )
    #sleep(3)
    bf.Keystroke_Appium([ [ ( 'Android keystroke' , 'action' , 'gO Back' , False , False ) ] ] )
    #sleep(3)
    bf.Keystroke_Appium([ [ ( 'Android keystroke' , 'action' , 'go back' , False , False ) ] ] )
    #sleep(3)
    bf.Click_Element_Appium([ [ ( 'id' , 'element parameter' , 'com.google.android.googlequicksearchbox:id/search_widget_hotword_prompt' , False , False ) ] ] )
    #sleep(3)
    bf.Enter_Text_Appium([ [ ( 'id' , 'element parameter' , 'com.google.android.googlequicksearchbox:id/search_box' , False , False ), ( 'text' , 'action' , 'camera' , False , False )  ] ] )
    #sleep(3)
    bf.Keystroke_Appium([ [ ( 'Android keystroke' , 'action' , 'reTurN' , False , False ) ] ] )
    #sleep(3)
    bf.close()

def Connect_To_MuxBoard():
    port_number = "2"
    ConnectDisconnectDevice('reset')
    result = Get_Port_To_Connect(port_number)
    
    for each_item in result:
        print each_item
        ConnectDisconnectDevice(1,int(each_item),'m')
        sleep(10)
        ConnectedDeviceAction()
       # ConnectDisconnectDevice(0,int(each_item),'m')
    
Connect_To_MuxBoard()