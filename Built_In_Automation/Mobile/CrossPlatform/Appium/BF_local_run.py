

from Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf
from appium import webdriver

#bf.launch_ios_app()
bf.launch_and_start_driver('com.assetscience.androidprodiagnostics','com.assetscience.recell.device.android.prodiagnostics.MainActivity')
bf.Click_Element([['accessibility_id','More options']])
bf.close()