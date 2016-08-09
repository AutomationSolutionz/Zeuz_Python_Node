

from Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf
from appium import webdriver

#bf.launch_ios_app()
bf.launch_and_start_driver('com.assetscience.androidprodiagnostics','com.assetscience.recell.device.android.prodiagnostics.MainActivity')
#bf.Click_Element([['accessibility_id','More options']])
#bf.Click_Element([['name','OK']])
#bf.Click_Element([['id','android:id/button3']])
#bf.Click_Element([['name','SEND RESULTS']])
#bf.Just_Click('id','android:id/button3')
#bf.Just_Click('name','SEND RESULTS')
bf.Sequential_Actions([[[['name','SEND RESULTS']],['click','action','click',False,False]]])
bf.close()