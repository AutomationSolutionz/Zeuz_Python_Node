# Android environment
from lxml.html.diff import tag_token
from appium import webdriver
import os , sys, time, inspect
from Utilities import CommonUtil
from Automation.Mobile.Android.adb_calls import adbOptions
from Automation.Web.SeleniumAutomation import clickInteraction,locateInteraction
from appium.webdriver.common.touch_action import TouchAction
from django.test.html import Element

#if local_run is True, no logging will be recorded to the web server.  Only local print will be displayed
#local_run = True
local_run = False


def launch(package_name,activity_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
        CommonUtil.ExecLog(sModuleInfo,"Trying to open the app",1,local_run)
        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        df = adbOptions.get_android_version()
        CommonUtil.ExecLog(sModuleInfo,df,1,local_run)
        #adbOptions.kill_adb_server()
        desired_caps['platformVersion'] = df
        df = adbOptions.get_device_model()
        CommonUtil.ExecLog(sModuleInfo,df,1,local_run)
        #adbOptions.kill_adb_server()
        desired_caps['deviceName'] = df
        desired_caps['appPackage'] = package_name
        desired_caps['appActivity'] = activity_name
        driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        global driver
        CommonUtil.ExecLog(sModuleInfo,"Opened the app successfully",1,local_run)
        time.sleep(2)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to start WebDriver. %s"%Error_Detail, 3,local_run)
        return "failed"

def close():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to close the app",1,local_run)
        driver.close_app()
        CommonUtil.ExecLog(sModuleInfo,"Closed the app successfully",1,local_run)
        driver.quit()
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to close the driver. %s"%Error_Detail, 3,local_run)
        return "failed"

def go_back():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to go back",1,local_run)
        driver.back()
        CommonUtil.ExecLog(sModuleInfo,"Went back successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to go back. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_id(_id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by id: %s"%_id,1,local_run)
        elem = driver.find_element_by_id(_id)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by id: %s"%_id,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_name(_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by name: %s"%_name,1,local_run)
        elem = driver.find_element_by_name(_name)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by name: %s"%_name,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_class_name(_class):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by class: %s"%_class,1,local_run)
        elem = driver.find_element_by_class_name(_class)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by class: %s"%_class,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_xpath(_classpath):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by xpath: %s"%_classpath,1,local_run)
        elem = driver.find_element_by_xpath(_classpath)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by class: %s"%_classpath,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def click_element_by_accessibility_id(_id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by accessibility id: %s"%_id,1,local_run)
        elem = driver.find_element_by_accessibility_id(_id)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on element by accessibility id: %s"%_id,1,local_run)
        elem.click()
        CommonUtil.ExecLog(sModuleInfo,"Clicked on element successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def confirm_right():
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to confirm the right menu options",1,local_run)
        click_element_by_id("ca.bellmedia.bnngo:id/action_right_toggle")
        check_element_by_id("ca.bellmedia.bnngo:id/rdo_stock")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Stock Lookup'",1,local_run)
        check_element_by_id("ca.bellmedia.bnngo:id/rdo_twitter")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Twitter'",1,local_run)
        check_element_by_id("ca.bellmedia.bnngo:id/rdo_tv")
        CommonUtil.ExecLog(sModuleInfo,"The right menu has 'Live'",1,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Confirmed the right menu items successfully",1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the right menu options. %s"%Error_Detail, 3,local_run)
        return "failed"

def go_left(section_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to go to the left menu section: %s"%section_name,1,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on left menu",1,local_run)
        click_element_by_id("android:id/home")
        CommonUtil.ExecLog(sModuleInfo,"Trying to click on the section: %s"%section_name,1,local_run)
        click_element_by_name(section_name)
        CommonUtil.ExecLog(sModuleInfo,"Clicked on the left menu section",1,local_run)
        CommonUtil.ExecLog(sModuleInfo,"Trying to match the section: %s"%section_name,1,local_run)
        elem = driver.find_element_by_id("android:id/action_bar_title")
        if elem.text == section_name:
            CommonUtil.ExecLog(sModuleInfo,"Opened the section - %s successfully"%section_name,1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to confirm the right menu options. %s"%Error_Detail, 3,local_run)
        return "failed"

def check_element_by_id(_id):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        CommonUtil.ExecLog(sModuleInfo,"Trying to find element by id: %s"%_id,1,local_run)
        elem = driver.find_elements_by_id(_id)
        if not elem:
            CommonUtil.ExecLog(sModuleInfo,"Element by id : %s not found"%_id,1,local_run)
        elif elem[0].is_displayed():
            click_element_by_id(_id)
            CommonUtil.ExecLog(sModuleInfo,"Element by id : %s found"%_id,1,local_run)
        return "Passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return "failed"

def select_base_car(car_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        clickInteraction.Click_By_Parameter_And_Value('class','changebtn btn')
        time.sleep(1)
        parent_element =locateInteraction.Locate_Element_By_ID('comp-popup-title')
        Model_drop_down =locateInteraction.Locate_Element_By_Parameter_Value('role','combobox',parent_element)
        Model_drop_down.click()
        #selecting the model
        CommonUtil.ExecLog(sModuleInfo,"Selecting car model: %s"%car_data['model'],1,local_run)
        parent_element=locateInteraction.Locate_Element_By_ID('x-auto-1')
        clickInteraction.Click_Element_By_Name(car_data['model'],parent_element)
        CommonUtil.ExecLog(sModuleInfo,"Selected car model: %s"%car_data['model'],1,local_run)
        #selecting the year
        parent_element =locateInteraction.Locate_Element_By_ID('comp-popup-title')
        Model_drop_down =locateInteraction.Locate_Element_By_Parameter_Value('role','combobox',parent_element,True)
        Model_drop_down[1].click()
        CommonUtil.ExecLog(sModuleInfo,"Selecting car year: %s"%car_data['year'],1,local_run)
        # parent_element=locateInteraction.Locate_Element_By_ID('x-auto-4')
        # parent_element.click()
        clickInteraction.Click_Element_By_Name(car_data['year'],parent_element)
        CommonUtil.ExecLog(sModuleInfo,"Selected car year: %s"%car_data['year'],1,local_run)
        #selecting the version
        panel_drop_down =locateInteraction.Locate_Element_By_Parameter_Value('class','pnl-trim')
        table_object=locateInteraction.Locate_Element_By_Tag('table',panel_drop_down,)
        version_text=locateInteraction.Locate_Element_In_Table_By_Text(car_data['version'],table_object)
        version_text.click()
        time.sleep(10)
        return True
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return False

def select_car(car_data,index):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        div_name_config = 'competitorgridview-selection-changebtn' + str(index - 1)
        _button_parent_element=locateInteraction.Locate_Element_By_ID(div_name_config)
        change_button=locateInteraction.Locate_Element_By_Tag('button',_button_parent_element)
        change_button.click()
        parent_element=locateInteraction.Locate_Element_By_Class('vehicleSelectionPopup')
        all_children=locateInteraction.Locate_All_Children(parent_element)

        if all_children:
            first_div=locateInteraction.Locate_All_Children(all_children[0])
            popup_selection=locateInteraction.Locate_Element_By_Class('compare-ptip-selection',first_div[2])
            t_body_tag=locateInteraction.Locate_Element_By_Tag('tbody',popup_selection)
            all_rows=locateInteraction.Locate_All_Children(t_body_tag)
            for _i,e in enumerate(all_rows):
                desired_input=locateInteraction.Locate_Element_By_TAG_Under_Specific_Element('input',e)
                desired_input.click()
                all_tds=locateInteraction.Locate_All_Children(e)
                if not all_tds:
                    CommonUtil.ExecLog(sModuleInfo,"Found not child elements in row",3,local_run)
                    return False
                all_divs=locateInteraction.Locate_Element_By_TAG_Under_Specific_Element('div',all_tds[1],True)
                if not all_divs:
                    CommonUtil.ExecLog(sModuleInfo, "Found not child elements in columns", 3, local_run)
                    return False
                if _i==0:
                    selected_data=car_data['year']
		    time.sleep(1)
                    CommonUtil.ExecLog(sModuleInfo,"Going to select the year of car %d"%index,1,local_run)
                elif _i==1:
                    selected_data=car_data['make']
		    time.sleep(1)
                    CommonUtil.ExecLog(sModuleInfo, "Going to select the make of car %d" % index, 1, local_run)
                elif _i==2:
                    selected_data=car_data['model']
		    time.sleep(1)
                    CommonUtil.ExecLog(sModuleInfo, "Going to select the model of car %d" % index, 1, local_run)
                elif _i==3:
                    selected_data=car_data['trim']
		    time.sleep(5)
                    CommonUtil.ExecLog(sModuleInfo, "Going to select the trim of car %d" % index, 1, local_run)
                else:
                    selected_data=''
                    CommonUtil.ExecLog(sModuleInfo, "Nothing to select for car %d" % index, 1, local_run)

                if _i in [0,1,2,3]:
                    clickInteraction.Click_Element_By_Name(selected_data,all_divs[1])

                if _i==0:
                    CommonUtil.ExecLog(sModuleInfo, "Selected the year of car %d, %s" %(index,selected_data), 1, local_run)
                elif _i==1:
                    CommonUtil.ExecLog(sModuleInfo, "Selected the make of car %d, %s" % (index, selected_data), 1,local_run)
                elif _i==2:
                    CommonUtil.ExecLog(sModuleInfo, "Selected the model of car %d, %s" % (index, selected_data), 1,local_run)
                elif _i==3:
                    CommonUtil.ExecLog(sModuleInfo, "Selected the trim of car %d, %s" % (index, selected_data), 1,local_run)
                else:
                    CommonUtil.ExecLog(sModuleInfo, "Nothing was selected of car %d, %s" % (index, selected_data), 1,local_run)
            return True
        else:
            CommonUtil.ExecLog(sModuleInfo, "Vehicle Selection Popup was not there", 1, local_run)
            return False

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to click on the element. %s"%Error_Detail, 3,local_run)
        return False

def read_data_from_page(tag_list):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        total_list=[]
        for e in tag_list:
            #print e[1]
            table_object=locateInteraction.Locate_Element_By_ID('AscAbstractGrid-Table')
            m=locateInteraction.Locate_Element_By_Parameter_Value('class','group expanded',table_object,multiple=True)
            ls =filter(lambda x:x.find_element_by_class_name('title').text.lower()==e[1].lower(),m)
            #take the values of the ls
            #get the table reference first
            #table_ref=locateInteraction.Locate_Element_By_Parameter_Value('class','group-body',ls[0])
            #get_all_the_rows
            all_rows=locateInteraction.Locate_Element_By_Tag('tr',ls[0],multiple=True)

            for i in all_rows:
                final_data=[]
                #find all td
                all_tds=locateInteraction.Locate_Element_By_Tag('td',i,True)
                filtered_from_nissan_advantage=filter(lambda x:'col2a' not in x.get_attribute('class'),all_tds)
                if filtered_from_nissan_advantage:
                    tag_name=filtered_from_nissan_advantage[0].text
                    count=1
                    for _i in filtered_from_nissan_advantage[1:]:
                        final_data.append((tag_name,'car'+str(count),_i.text,False,False))
                        count+=1

                if final_data:
                    final_data=sorted(final_data,key=lambda x:x[1])
                    total_list=list(total_list+final_data)
        return total_list
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to read the data. %s"%Error_Detail, 3,local_run)
        return False

def lock_unlock_car(car_num,mode=False):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        car_lock_button='lock-button-'+str(car_num-1)
        lockButton=locateInteraction.Locate_Element_By_ID(car_lock_button)
        CommonUtil.ExecLog(sModuleInfo,"Lock button located",1,local_run)
        if mode:
            #will be locked.so check for that locked is not present in there.
            if 'locked' not in lockButton.get_attribute('class'):
                CommonUtil.ExecLog(sModuleInfo,"Lock Button unlocked",1,local_run)
                lockButton.click()
                CommonUtil.ExecLog(sModuleInfo,"Lock Button clicked",1,local_run)
                lockButton=locateInteraction.Locate_Element_By_ID(car_lock_button)
                if 'locked' in lockButton.get_attribute('class'):
                    CommonUtil.ExecLog(sModuleInfo,'Lock Button locked successfully',1,local_run)
                    return True
                else:
                    CommonUtil.ExecLog(sModuleInfo,'Lock Button is not locked',3,local_run)
                    return False
            else:
                CommonUtil.ExecLog(sModuleInfo,"Lock Button locked already",1,local_run)
                return True
        else:
            if 'locked' not in lockButton.get_attribute('class'):
                CommonUtil.ExecLog(sModuleInfo,"Lock Button unlocked already",1,local_run)
                return True
            else:
                CommonUtil.ExecLog(sModuleInfo,"Lock Button locked",1,local_run)
                lockButton.click()
                CommonUtil.ExecLog(sModuleInfo,"Lock Button clicked",1,local_run)
                lockButton=locateInteraction.Locate_Element_By_ID(car_lock_button)
                if 'locked' not  in lockButton.get_attribute('class'):
                    CommonUtil.ExecLog(sModuleInfo,'Lock Button unlocked successfully',1,local_run)
                    return True
                else:
                    CommonUtil.ExecLog(sModuleInfo,'Lock Button is still locked',3,local_run)
                    return False
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to unlock. %s"%Error_Detail, 3,local_run)
        return False

def open_detail_pop_up(tag_to_click,description_to_match):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        print tag_to_click,description_to_match
        table_ref=locateInteraction.Locate_Element_By_ID('AscAbstractGrid-Table')
        all_tds=locateInteraction.Locate_Element_By_Tag('td',table_ref,multiple=True)
        desired_td=filter(lambda x:'hasFeature' in x.get_attribute('class') and x.text==tag_to_click,all_tds)
        if desired_td:
            CommonUtil.ExecLog(sModuleInfo,"Clickable feature found with text: %s"%(tag_to_click),1,local_run)
            #clickInteraction.scrollTo(0,desired_td[0].location['y'])
            desired_td[0].click()
            CommonUtil.ExecLog(sModuleInfo,"Clicked feature found with text: %s"%(tag_to_click),1,local_run)
            #get the desired data
            description_tab=locateInteraction.Locate_Element_By_ID('compare-ptip-features-description')
            data_set=[('tag',tag_to_click,False,False),('description',description_tab.text,False,False)]
            return data_set
        else:
            CommonUtil.ExecLog(sModuleInfo,"No column is found with this criteria",3,local_run)
            return False
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to open detail popup. %s"%Error_Detail, 3,local_run)
        return False

def check_nissan_adv_tag(tag_given):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        table_ref=locateInteraction.Locate_Element_By_ID('AscAbstractGrid-Table')
        all_tds=locateInteraction.Locate_Element_By_Tag('tr',table_ref,multiple=True)
        filter_tds=filter(lambda x: tag_given in x.text,all_tds)
        if filter_tds:
            d_one=filter_tds[-1]
            all_trs=locateInteraction.Locate_Element_By_Tag('td',d_one,multiple=True)
            if all_trs:
                nissan_tag=filter(lambda x: 'col2aAdv' in x.get_attribute('class'),all_trs)
                if nissan_tag:
                    CommonUtil.ExecLog(sModuleInfo,"Nissan advantage tag is found for: %s"%tag_given,1,local_run)
                    return True
                else:
                    CommonUtil.ExecLog(sModuleInfo,"Nissan advantage tag is not found for: %s"%tag_given,1,local_run)
                    return False
            else:
                CommonUtil.ExecLog(sModuleInfo,"No column is found under the given tag: %s"%tag_given,3,local_run)
                return False
        else:
            CommonUtil.ExecLog(sModuleInfo,"No row is found with the given tag: %s"%tag_given,3,local_run)
            return False
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to locate nissan tag on the element. %s"%Error_Detail, 3,local_run)
        return False
