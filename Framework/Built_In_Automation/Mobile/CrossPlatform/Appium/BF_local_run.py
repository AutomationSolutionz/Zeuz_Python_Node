

from Built_In_Automation.Mobile.CrossPlatform.Appium import BuiltInFunctions as bf
#from Built_In_Automation.Mobile.CrossPlatform.Appium import clickinteraction as ci
from appium import webdriver

bf.launch('com.google.android.youtube', 'com.google.android.youtube.HomeActivity')
#bf.Swipe_Appium([ [ ( 'swipe' , 'action' , 'down' , False , False ) ] ] )
#bf.Go_Back_Appium([ [ ( 'go_back' , 'action' , 'go_back' , False , False ) ] ] )
bf.Keystroke_Appium([ [ ( 'Android keystroke' , 'action' , 'go back' , False , False ) ] ] )
bf.Keystroke_Appium([ [ ( 'Android keystroke' , 'action' , 'gO Back' , False , False ) ] ] )
bf.Keystroke_Appium([ [ ( 'Android keystroke' , 'action' , 'go back' , False , False ) ] ] )


bf.Click_Element_Appium([ [ ( 'id' , 'element parameter' , 'com.google.android.googlequicksearchbox:id/search_widget_hotword_prompt' , False , False ) ] ] )
bf.Enter_Text_Appium([ [ ( 'id' , 'element parameter' , 'com.google.android.googlequicksearchbox:id/search_box' , False , False ), ( 'text' , 'action' , 'camera' , False , False )  ] ] )
bf.Keystroke_Appium([ [ ( 'Android keystroke' , 'action' , 'reTurN' , False , False ) ] ] )
bf.Validate_Text_Appium([ [ ( 'content-desc' , 'element properties', 'Camera Store' , False , False ) , ( 'validate partial text' , 'action' , 'Camera Store' , False , False ) ] ] )

bf.close()

#bf.launch_ios_app()
#bf.launch('com.assetscience.androidprodiagnostics','com.assetscience.recell.device.android.prodiagnostics.MainActivity')
#bf.locate_element_by_accessibility_id('More options')
#bf.Get_Element_Appium('class_name', 'android.widget.FrameLayout')#, reference_parameter, reference_value, reference_is_parent_or_child, get_all_unvalidated_elements)
#bf.Get_Element_Appium('id', 'com.assetscience.androidprodiagnostics:id/resumeButtonView', 'class_name', 'android.widget.LinearLayout', 'parent')
#bf.Get_Element_Appium('id', 'com.assetscience.androidprodiagnostics:id/resumeButtonView', 'class_name', 'android.widget.LinearLayout', 'child')
#bf.Tap_Appium([ [ ( 'accessibility_id' , '' , 'More options' , False , False ) ] ] )

#bf.Get_All_Elements_Appium('accessibility_id','More options')
#bf.Sequential_Actions([[['click','action','click',False,False]],[['accessibility_id','','More options',False,False]]])
#bf.Sequential_Actions([[['accessibility_id','More options'],['click','action','click',False,False]]])
#bf.Click_Element([['name','OK']])
#bf.Click_Element([['id','android:id/button3']])
#bf.Click_Element([['accessibility_id', '', 'More options',False,False]])
#bf.Click_Element([['name','SEND RESULTS']])
#bf.Just_Click('id','android:id/button3')
#bf.Just_Click('name','SEND RESULTS')
#bf.Sequential_Actions([[[['name','SEND RESULTS']],['click','action','click',False,False]]])
#bf.launch_and_start_driver('com.bunz', 'com.bunz.activity.LaunchActivity')
#bf.Sequential_Actions([[[u'resource-id', u'', u'com.bunz:id/btn_login', False, False], [u'click', u'action', u'click', False, False]], [[u'resource-id', u'', u'com.bunz:id/btn_login_email', False, False], [u'click', u'action', u'click', False, False]], [[u'wait', u'action', u'5', False, False], [u'wait', u'and', u'see', False, False]], [[u'resource-id', u'', u'com.bunz:id/edt_email', False, False], [u'click', u'action', u'click', False, False]], [[u'wait', u'action', u'5', False, False], [u'wait', u'and', u'see', False, False]], [[u'resource-id', u'', u'com.bunz:id/edt_email', False, False], [u'text', u'action', u'test@bunz.com', False, False]], [[u'resource-id', u'', u'com.bunz:id/edt_password', False, False], [u'click', u'action', u'click', False, False]], [[u'wait', u'action', u'5', False, False], [u'wait', u'and', u'see', False, False]], [[u'resource-id', u'', u'com.bunz:id/edt_password', False, False], [u'text', u'action', u'password', False, False]], [[u'resource-id', u'', u'com.bunz:id/btn_login_email', False, False], [u'click', u'action', u'click', False, False]]])
#bf.Sequential_Actions([[['click','action','click'],['accessibility_id','','Navigate up']]])
#bf.Sequential_Actions([[['click','action','click'],['name','','Login']],[['click','action','click'],['name','', 'Email Login']], [('id', '', 'com.bunz:id/edt_email'), ('text', 'action', 'okay')]])
"""bf.Click_Element([[['id', '', 'com.bunz:id/txt_next']]])
bf.Click_Element([[['id', '', 'com.bunz:id/txt_next']]])
bf.Click_Element([[['id', '', 'com.bunz:id/txt_next']]])
bf.Click_Element([[['id', '', 'com.bunz:id/txt_next']]])
bf.Click_Element([[['name', '', 'Login here']]])
#ci.click_element_by_id(bf.driver, 'com.bunz:id/txt_next')
bf.Click_Element([[['name', '', 'Login']]])
bf.Click_Element([[['name', '', 'Email Login']]])
bf.Set_Text([[('id', '', 'com.bunz:id/edt_email'), ('text', '', 'okay')]])
bf.Set_Text([[('id', '', 'com.bunz:id/edt_password'), ('text', '', 'test')]])
bf.Click_Element([[['name', '', 'Login to Bunz!']]])
bf.wait(10)
bf.Click_Element([[['accessibility_id', '', 'Navigate up']]])
bf.Click_Element([[['name', '', 'Chats']]])
bf.Click_Element([[['accessibility_id', '', 'Navigate up']]])
bf.Click_Element([[['name', '', 'Settings']]])
bf.Click_Element([[['name', '', 'City']]])"""
#bf.Wait(5)
#bf.Swipe()
#bf.Sequential_Actions([[['wait','action',float('5')],[]], [['swipe','action','swipe'],[]], [['tap','action','tap'], ['id','','com.bunz:id/fab_create_post']]])
#bf.close()

"""bf.launch_and_start_driver('com.android.settings', 'com.android.settings.Settings')
bf.Swipe([])
bf.Swipe([])
bf.Click_Element([['name', 'Backup & reset']])
bf.Click_Element([['name', 'Factory data reset']])
bf.Click_Element([['name', 'Reset phone']])
bf.Click_Element([['name', 'Erase everything']])
bf.close()"""