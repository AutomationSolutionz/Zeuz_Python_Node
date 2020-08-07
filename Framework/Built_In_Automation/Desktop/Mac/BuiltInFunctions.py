# coding=utf-8
# -*- coding: cp1252 -*-
# codfing=utf-8


import sys, os, time, inspect
import glob

sys.path.append(os.path.dirname(__file__))
from Framework.Utilities import CommonUtil
import pyautogui as gui  # https://pyautogui.readthedocs.io/en/latest/
from Framework.Utilities.decorators import logger
from Framework.Built_In_Automation.Shared_Resources import (
    BuiltInFunctionSharedResources as Shared_Resources,
)
from Framework.Built_In_Automation.Shared_Resources import LocateElement
from Framework.Utilities.CommonUtil import (
    passed_tag_list,
    failed_tag_list,
    skipped_tag_list,
)

import inspect, time, datetime, os, sys
from os import system
from _elementtree import Element  # What is this for?
from Framework.Utilities import CommonUtil

MODULE_NAME = inspect.getmodulename(__file__)


from appscript import *

# import ipython

import os
import sys

sys.path.append("..")

import time
import inspect

Global = Globals.ObjectIDs()
# from EasyDialogs import ProgressBar


"""Finding Objects Function"""


@logger
def get_all_obj_main_win(MenuOrWindow=None):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        all_obj = []
        if MenuOrWindow == None:
            MainItems = (
                app(u"System Events").processes[u"ProductName"].UI_elements.get()
            )
            for eachWind in MainItems:
                try:
                    if (
                        eachWind.attributes[u"AXIdentifier"].value.get() == "mainWindow"
                    ):  #'_NS:6':
                        parent_ID = eachWind.UI_elements.get()
                except:
                    pass
        elif MenuOrWindow == "toast":
            MainItems = (
                app(u"System Events").processes[u"ProductName"].UI_elements.get()
            )
            for eachWind in MainItems:
                try:
                    if eachWind.title.get() == "Window":  #'_NS:105':
                        parent_ID = eachWind.UI_elements.get()
                except:
                    pass
        else:
            parent_ID = (
                app(u"System Events")
                .processes[u"ProductName"]
                .menu_bars[1]
                .UI_elements.get()
            )

        # parent =  get_child_obj(parent_ID)
        all_obj = all_obj + parent_ID
        for i in range(13):
            Child = get_child_obj(parent_ID)
            if Child != None and Child != "Critical":
                all_obj = all_obj + Child
            parent_ID = Child
        #        child_1 = get_child_obj(parent)
        #        child_2 = get_child_obj(child_1)
        #        child_3 = get_child_obj(child_2)
        #        child_4 = get_child_obj(child_3)
        #        child_5 = get_child_obj(child_4)
        #        child_6 = get_child_obj(child_5)
        #        child_7 = get_child_obj(child_6)
        #
        #        all_obj = parent_ID + parent + child_1 + child_2 + child_3 + child_4 + child_5 + child_6 + child_7
        total_obj_count = len(all_obj)
        #        print("%s > Total Elements Found (%s)" %(sModuleInfo,total_obj_count))
        #        CommonUtil.ExecLog(sModuleInfo,"Total Elements Found (%s)" %total_obj_count,1)
        Globals.Object_List = all_obj
        return all_obj

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def get_child_obj(obj_list):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        get_child_obj = []
        if obj_list != None:
            obj_list_size = len(obj_list)
            for i in range(obj_list_size):
                obj = obj_list[i]
                try:
                    child_obj = obj.attributes[u"AXChildren"].value.get()
                    if child_obj != []:
                        get_child_obj = get_child_obj + child_obj

                except:
                    pass
        #                            Obj_without_child = []
        #                            Obj_without_child.append(obj)
        #                            get_child_obj = get_child_obj + Obj_without_child
        if get_child_obj != []:
            return get_child_obj
        else:
            return None
    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def get_elem_with_role_nd_title(obj_list, role_type, elem_title):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        obj_list_size = len(obj_list)
        for i in range(obj_list_size):
            obj = obj_list[i]
            try:
                role_name = get_role_of_element(obj)
                elem_name = get_title_of_element(obj)
            except:
                a = 1
            # lenght = len(child_obj)
            #            print(role_name)
            #            print(elem_name)
            if (role_name == role_type) and (elem_title == elem_name):

                return obj
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


@logger
def get_elem_with_role(obj_list, role_type):
    # there is a possiblity of having duplicate element so we need to build our list and send as list and not as obj
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        elem_with_role = []

        for temp_obj in obj_list:
            try:
                role_name = get_role_of_element(temp_obj)
            #                print("role of element is :")
            #                print(role_name)
            #                print(role_type)
            except:
                a = 1
            if role_name == role_type:
                #                print("matched")
                elem_with_role.append(temp_obj)
                # print(elem_with_role)
            else:
                a = 1
                # print("didnt match")
        # print(elem_with_role)
        return elem_with_role
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


@logger
def get_obj_list_txt_value_nd_obj_id(obj_list, txt_value, obj_id):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        # all_obj =  get_all_obj_main_win()
        all_obj_with_id = get_obj_with_given_id(obj_list, obj_id)
        get_all_txt_obj = get_elem_with_role(all_obj_with_id, "AXStaticText")

        result_list = []
        for element in get_all_txt_obj:

            temp = get_value_of_element(element)
            #         print("printing values")
            #         print(temp)
            #         print(txt_value)
            if txt_value in temp:
                result_list.append(element)
        return result_list
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


@logger
def get_obj_list_txt_value(obj_list, txt_value):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        result_list = []
        for element in obj_list:

            temp = get_value_of_element(element)
            if txt_value in temp:
                result_list.append(element)
        return result_list
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


@logger
def get_elem_with_role_nd_index(obj_list, elem_index):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        obj_list_size = len(obj_list)
        for i in range(obj_list_size):
            obj = obj_list[i]
            try:
                obj_to_string = str(obj)
            except:
                a = 1
            if elem_index in obj_to_string:
                return obj
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


@logger
def Find_Element(
    elem_id=None,
    elem_path=None,
    elem_role=None,
    elem_value=None,
    elem_position=None,
    MenuOrWindow=None,
):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        Element = [
            Key
            for Key, Value in Global.Ids.items()
            if Value == elem_id or Value == elem_path
        ]
        for N in Element:
            if "DeviceMenu" in N:
                MenuOrWindow = "Menu"

        @logger
        def Find(obj_list, elem_id, elem_path):
            for obj_temp in obj_list:
                obj_id_temp = False
                try:
                    obj_id_temp = obj_temp.attributes[u"AXIdentifier"].value.get()
                except:
                    a = 1
                if str(obj_temp) == str(elem_path):
                    obj_id_list.append(obj_temp)
                    elem_id = elem_path
                if str(CommonUtil.to_unicode(obj_id_temp)) == elem_id:
                    obj_id_list.append(obj_temp)
            return obj_id_list

        ###If length of found elements is zero###

        obj_id_list = []

        obj_list = Globals.Object_List
        obj_id_list = Find(obj_list, elem_id, elem_path)
        if obj_id_list == []:

            # print("Calling get_all_obj function")
            obj_list = get_all_obj_main_win(MenuOrWindow)
            # print(obj_list)
            obj_id_list = Find(obj_list, elem_id, elem_path)

        ObjsLen = len(obj_id_list)
        if ObjsLen == 0:
            # print("%s > Object of id/path (%s) not found!" %(sModuleInfo,Element))
            # CommonUtil.ExecLog(sModuleInfo,"Object of id/pth (%s) not found!" %(Element),3)
            return False

        ###If length of found elements is one###
        if ObjsLen == 1 or ObjsLen > 1:
            # print("%s > (%s) Object/s of id (%s) found!" %(sModuleInfo,ObjsLen,Element))
            # CommonUtil.ExecLog(sModuleInfo,"(%s) Object/s of id (%s) found!" %(ObjsLen,Element),1)
            FoundObj = []
            if elem_role != None:
                for eachElem in obj_id_list:
                    Attribute = get_role_of_element(eachElem)
                    if Attribute == elem_role:
                        FoundObj.append(eachElem)
                        return FoundObj

            elif elem_value != None:
                for eachElem in obj_id_list:
                    Attribute = get_value_of_element(eachElem)
                    if Attribute == elem_role:
                        FoundObj.append(eachElem)
                        return FoundObj

            if (elem_role != None or elem_value != None) and (FoundObj == []):
                return FoundObj
            else:

                return obj_id_list

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


"""Finding Attributes Functions"""


@logger
def get_title_of_element(id_path):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        title_of_ele = id_path.title.get()
        return True
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


@logger
def get_role_of_element(id_path):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        role_of_ele = id_path.role.get()
        return role_of_ele
    except Exception as e:
        print("Exception : ", e)
        return "Critical"


@logger
def get_value_of_element(id_path):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        value_of_ele = id_path.value.get()
        return value_of_ele
    except Exception as e:
        print("Exception : ", e)
        return "Critical"


@logger
def get_position_of_element(id_path):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        postion_of_ele = id_path.position.get()
        return postion_of_ele
    except Exception as e:
        print("Exception : ", e)
        return "Critical"


"""UI Automation Functions For Application"""


@logger
def is_app_running(app_name):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        process_list = app(u"System Events").processes.name.get()
        if app_name in process_list:
            return True
        else:
            return False

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def Run_Application(app_name):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        if is_app_running(app_name) == False:
            app(app_name).activate()
            count = 0
            while count != 8:
                time.sleep(0.5)
                count = count + 1

                if is_app_running(app_name) == True:
                    return True
                elif count == 8:
                    return "Timeout"
        else:
            return True

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def close_app(app_name):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        if is_app_running(app_name) == True:
            count = 0
            while count == 0:
                app(app_name).quit()
                time.sleep(0.5)
                count = count + 1
                if is_app_running(app_name) == False:
                    return True
                if count == 8:
                    os.system("%s '%s' " % ("killall -9", app_name))
                    time.sleep(1)
                    if is_app_running(app_name) == False:
                        return True
                    else:
                        return False
        else:
            return True
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


"""UI Automation Functions For Elements"""


@logger
def wait_for_obj_to_appear(
    ElemId=None,
    ElemPath=None,
    ElemRole=None,
    ElemValue=None,
    ElemPosition=None,
    Timeout=15,
):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        ElementName = [
            Key
            for Key, Value in Global.Ids.items()
            if Value == ElemId or Value == ElemPath
        ]
        element = Find_Element(
            elem_id=ElemId,
            elem_path=ElemPath,
            elem_role=ElemRole,
            elem_value=ElemValue,
            elem_position=ElemPosition,
        )
        wait = 0
        while element == [] or element == False:
            time.sleep(1)
            wait = wait + 1
            if wait == Timeout:
                #                print("%s > Timeout: Element (%s) was not found in (%s) seconds!" %(sModuleInfo,ElementName,wait))
                #                CommonUtil.ExecLog(sModuleInfo,"Timeout: Element (%s) was not found in (%s) seconds!" %(ElementName,wait),3)
                return False
            element = Find_Element(
                elem_id=ElemId,
                elem_role=ElemRole,
                elem_value=ElemValue,
                elem_position=ElemPosition,
            )
        #        print("%s > Element (%s) was found in (%s) seconds!" %(sModuleInfo,ElementName,wait))
        #        CommonUtil.ExecLog(sModuleInfo,"Element (%s) was found in (%s) seconds!" %(ElementName,wait),3)
        return True

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def check_uncheck_box(
    ElemId=None,
    ElemPath=None,
    check_uncheck=None,
    ElemRole=None,
    ElemValue=None,
    ElemPosition=None,
):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        element = Find_Element(
            elem_id=ElemId,
            elem_path=ElemPath,
            elem_role=ElemRole,
            elem_value=ElemValue,
            elem_position=ElemPosition,
        )
        if element != False and len(element) > 0:
            status = element[0].value.get()
            if check_uncheck == 1:
                if status == 1:
                    return True
                else:
                    element[0].click()

            elif check_uncheck == 0:
                if status == 0:
                    return True
                else:
                    element[0].click()

            status = element[0].value.get()
            if status == check_uncheck:
                return True
            else:
                return False
        else:
            return False

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def click_button(
    ElemId=None, ElemPath=None, ElemRole=None, ElemValue=None, ElemPosition=None
):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        ElementName = [
            Key
            for Key, Value in Global.Ids.items()
            if Value == ElemId or Value == ElemPath
        ]
        if ElemPath == None:
            element = Find_Element(
                elem_id=ElemId,
                elem_path=ElemPath,
                elem_role=ElemRole,
                elem_value=ElemValue,
                elem_position=ElemPosition,
            )
        else:
            element = [ElemPath]

        if element != False:
            if element[0].enabled.get() == True:
                element[0].click()
                #                print("%s > Button (%s) has been clicked" %(sModuleInfo,ElementName))
                CommonUtil.ExecLog(
                    sModuleInfo, "Button (%s) has been clicked" % ElementName, 1
                )
                return True
            else:
                #                print("%s > Button (%s) was not enabled" %(sModuleInfo,ElementName))
                CommonUtil.ExecLog(
                    sModuleInfo, "Button (%s) was not enabled" % ElementName, 1
                )
                return False
        else:
            #            print("%s > Button (%s) was not be found" %(sModuleInfo,ElementName))
            CommonUtil.ExecLog(
                sModuleInfo, "Button (%s) was not be found" % ElementName, 1
            )
            return False

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def click_given_loc_appscript(id_path):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

        @logger
        def get_clickable_location(id_path):
            sModuleInfo = (
                inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
            )
            try:
                clickable_position = []
                raw_position = id_path.position.get()
                raw_size = id_path.size.get()
                raw_position_x = int(raw_position[0])
                raw_position_y = int(raw_position[1])
                raw_size_x = int(raw_size[0])
                raw_size_y = int(raw_size[1])

                half_raw_size_x = raw_size_x / 2
                half_raw_size_y = raw_size_y / 2
                clickable_position_x = half_raw_size_x + raw_position_x
                clickable_position_y = half_raw_size_y + raw_position_y
                clickable_position = [clickable_position_x, clickable_position_y]
                return clickable_position

            except:
                print("Something went wrong ")
                return False

        ClickablePosition = get_clickable_location(id_path)
        x_position = ClickablePosition[0]
        y_position = ClickablePosition[1]

        print("performing mac click")
        app(u"System Events").processes[u"ProductName"].click(
            at=[x_position, y_position]
        )
        # print("%s > Button (%s) has been clicked" %(sModuleInfo,ElemId))
        # CommonUtil.ExecLog(sModuleInfo,"Button has been clicked",1)
        return True
    except Exception as e:
        print("Exception:", e)
        CommonUtil.ExecLog(sModuleInfo, "Exception in clicking: %s" % e, 3)
        return False


@logger
def is_check_box_enable_disabled(
    ElemId=None, ElemPath=None, ElemRole=None, ElemValue=None, ElemPosition=None
):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        ElementName = [
            Key
            for Key, Value in Global.Ids.items()
            if Value == ElemId or Value == ElemPath
        ]
        element = Find_Element(
            elem_id=ElemId,
            elem_path=ElemPath,
            elem_role=ElemRole,
            elem_value=ElemValue,
            elem_position=ElemPosition,
        )
        if element != False:
            enabled_disabled = element.enabled.get()
            return enabled_disabled
        else:
            return "Critical"

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def is_check_box_checked_unchecked(
    ElemId=None, ElemPath=None, ElemRole=None, ElemValue=None, ElemPosition=None
):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        ElementName = [
            Key
            for Key, Value in Global.Ids.items()
            if Value == ElemId or Value == ElemPath
        ]
        element = Find_Element(
            elem_id=ElemId,
            elem_path=ElemPath,
            elem_role=ElemRole,
            elem_value=ElemValue,
            elem_position=ElemPosition,
        )
        if element != False and len(element) > 0:
            status = element[0].value.get()
            return status
        else:
            return "Critical"

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def is_button_enabled_disabled(
    ElemId=None, ElemPath=None, ElemRole=None, ElemValue=None, ElemPosition=None
):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        ElementName = [
            Key
            for Key, Value in Global.Ids.items()
            if Value == ElemId or Value == ElemPath
        ]
        if ElemPath == None:
            element = Find_Element(
                elem_id=ElemId,
                elem_path=ElemPath,
                elem_role=ElemRole,
                elem_value=ElemValue,
                elem_position=ElemPosition,
            )
        else:
            element = [ElemPath]
        if element != False:
            enabled_disabled = element[0].enabled.get()
            return enabled_disabled
        else:
            return "Critical"

    except Exception as e:
        return CommonUtil.LogCriticalException(sModuleInfo, e)


@logger
def set_txt_value(id_path, txt):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        set_txt = id_path.value.set(txt)
        print("performed seting value to empty")
        return True
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


@logger
def set_txt_value_by_keystroke(id_path, txt):
    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        # set value with empty string
        #         print("seting the value to empty")
        #         os.system('~/Desktop/MouseTools -leftClick')
        print("calling set funcion to set the name to empty")
        set_txt_value(id_path, "")
        #         os.system('~/Desktop/MouseTools -leftClick')
        # get and click location
        print("getting clickable location")
        text_field_locaion_to_click = get_clickable_location(id_path)
        print("found clicable locaiton")

        click_given_loc(text_field_locaion_to_click)
        time.sleep(1)

        # keystroke the value in
        print("about to type keystroke")
        keystroke(txt)
        print("done keysroking")

        return True
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


@logger
def verify_txt_field_value(id_path, txt):
    print("we need to work on this")


@logger
def select_txt_field(id_path):
    print("need to do this")


@logger
def keystroke(txt):
    print("inside the keysroke module")
    try:
        print("activating bbl")
        app("ProductName").activate()
        print("performing keysroke")

        app(u"System Events").processes["ProductName"].keystroke(txt)
        #         print("clicking to make sure someething happens")
        #         os.system('~/Desktop/MouseTools -leftClick')
        return True
    except:
        print("Something went wrong ")
        return False


@logger
def click_given_loc(loc):

    try:
        sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
        app(u"ProductName").activate()
        x_position = loc[0]
        y_position = loc[1]

        print("moving to given position")
        os.system(
            "%s/MouseTools -x %s, -y %s"
            % (os.path.dirname(os.path.abspath(__file__)), x_position, y_position)
        )
        print("execuing actual mouse left click")
        os.system("~/Desktop/MouseTools -leftClick")
        print("clicked it")
        print("sleeing for 1 second")
        time.sleep(1)
        print("execuing actual mouse left click")
        os.system("~/Desktop/MouseTools -leftClick")
        print("clicked it second time and now waiting for 1 second")
        time.sleep(1)
    except Exception as e:
        print("%s > Exception Happened (%s)" % (sModuleInfo, e))
        CommonUtil.ExecLog(sModuleInfo, "Exception Happened (%s)" % e, 3)
        return False


@logger
def main():
    pass
    # print(get_all_obj_main_win())
    # print(Find_Element('newDeviceLanderPageContinueButton'))


#    print(wait_for_obj_to_appear(ElemId="_NS:20"))
#    print(is_button_enabled_disabled(ElemId = "_NS:20"))


#    print(click_button(ElemPath = Global.Ids["DesktopThumbnailVeiw"]))

#    print(Select_Media_Source("Test"))
#    import CommonUtil as C
#    C.ConnectDisconnectDevcie(1)
# print(click_button(ElemId = "_NS:10", ElemRole = "AXButton"))
#    MainItems = app(u'System Events').processes[u'ProductName'].UI_elements.get()
#    if len(MainItems) == 3:
#        ChildItem = app(u'System Events').processes[u'ProductName'].windows[1].UI_elements.get()
#        for each in ChildItem:
#            if each.attributes[u'AXIdentifier'].value.get() == "_NS:42":
#                print("Could not find progress bar, but got message box")
#                return "Pass"
#            if each.attributes[u'AXIdentifier'].value.get() == "_NS:94":
#                print("Progress Bar Found")
#    elif len(MainItems) < 3:
#        print("Toasted window did not appear")
#    l1 = Find_Element(elem_id="_NS:20")
#    for eachbtn in l1:
#        eachbtn.click()
# app(u'/System/Library/CoreServices/System Events.app').application_processes[u'ProductName'].windows[u'ProductName'].groups[1].groups[1].buttons[2].click()

main()
