

from Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf
from Built_In_Automation.Mobile.CrossPlatform.Appium import clickinteraction as ci
from appium import webdriver

#bf.launch_ios_app()
#bf.launch_and_start_driver('com.assetscience.androidprodiagnostics','com.assetscience.recell.device.android.prodiagnostics.MainActivity')
#bf.Sequential_Actions([[['click','action','click',False,False]],[['accessibility_id','','More options',False,False]]])
#bf.Sequential_Actions([[['accessibility_id','More options'],['click','action','click',False,False]]])
#bf.Click_Element([['name','OK']])
#bf.Click_Element([['id','android:id/button3']])
#bf.Click_Element([['accessibility_id', '', 'More options',False,False]])
#bf.Click_Element([['name','SEND RESULTS']])
#bf.Just_Click('id','android:id/button3')
#bf.Just_Click('name','SEND RESULTS')
#bf.Sequential_Actions([[[['name','SEND RESULTS']],['click','action','click',False,False]]])
bf.launch_and_start_driver('com.bunz', 'com.bunz.activity.LaunchActivity')
"""bf.Click_Element([[['id', '', 'com.bunz:id/txt_next']]])
bf.Click_Element([[['id', '', 'com.bunz:id/txt_next']]])
bf.Click_Element([[['id', '', 'com.bunz:id/txt_next']]])
bf.Click_Element([[['id', '', 'com.bunz:id/txt_next']]])
bf.Click_Element([[['name', '', 'Login here']]])"""
#ci.click_element_by_id(bf.driver, 'com.bunz:id/txt_next')
bf.Click_Element([[['name', '', 'Login']]])
bf.Click_Element([[['name', '', 'Email Login']]])
bf.Set_Text([[('id', '', 'com.bunz:id/edt_email'), ('text', '', 'okay')]])
bf.Set_Text([[('id', '', 'com.bunz:id/edt_password'), ('text', '', 'test')]])
bf.Click_Element([[['name', '', 'Login to Bunz!']]])
bf.wait(10)
"""bf.Click_Element([[['accessibility_id', '', 'Navigate up']]])
bf.Click_Element([[['name', '', 'Chats']]])
bf.Click_Element([[['accessibility_id', '', 'Navigate up']]])
bf.Click_Element([[['name', '', 'Settings']]])
bf.Click_Element([[['name', '', 'City']]])"""
bf.close()

"""bf.launch_and_start_driver('com.android.settings', 'com.android.settings.Settings')
bf.Swipe([])
bf.Swipe([])
bf.Click_Element([['name', 'Backup & reset']])
bf.Click_Element([['name', 'Factory data reset']])
bf.Click_Element([['name', 'Reset phone']])
bf.Click_Element([['name', 'Erase everything']])
bf.close()"""