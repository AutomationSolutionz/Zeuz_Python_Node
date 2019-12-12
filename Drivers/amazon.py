import os, sys
import inspect
from Framework.Utilities import CommonUtil
from Projects.Sample_Amazon_Testing import Amazon

from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list

MODULE_NAME = inspect.getmodulename(__file__)

def search_an_item_on_amazon(dependency,run_time_params,step_data,file_attachment,temp_q,screen_capture,device_info):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Search an Item on Amazon", 1)
        search_text=step_data[0][0][2]
        sTestStepReturnStatus = Amazon.Item_Search(search_text)

        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Successfully searched an item on Amazon", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Search an item on Amazon", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Unable to search an item on Amazon", 3)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Search an item on Amazon", 1)
            return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Search an item on Amazon", 1)
            return "failed"


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())


def add_an_item_to_cart_on_amazon(dependency,run_time_params,step_data,file_attachment,temp_q,screen_capture,device_info):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Add an Item to Cart on Amazon", 1)
        search_text=step_data[0][0][2]
        sTestStepReturnStatus = Amazon.Add_to_Cart(search_text)

        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Successfully Added an Item to Cart on Amazon", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Add an Item to Cart on Amazon", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Unable to add an item on Amazon", 3)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Add an Item to Cart on Amazon", 1)
            return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Add an item to cart on Amazon", 1)
            return sTestStepReturnStatus


    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())

def add_an_item_to_cart_on_amazon_using_selenium(dependency,run_time_params,step_data,file_attachment,temp_q,screen_capture,device_info):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    try:
        CommonUtil.ExecLog(sModuleInfo, "Enter: Step - Add an Item to Cart on Amazon Using Selenium", 1)
        sTestStepReturnStatus = Amazon.Add_to_Cart_Using_Selenium(step_data,file_attachment)

        if sTestStepReturnStatus in passed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Successfully Added an Item to Cart on Amazon", 1)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Add an Item to Cart on Amazon Using Selenium", 1)
            return sTestStepReturnStatus

        elif sTestStepReturnStatus in failed_tag_list:
            CommonUtil.ExecLog(sModuleInfo,"Unable to add an item on Amazon", 3)
            temp_q.put(sTestStepReturnStatus)
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Add an Item to Cart on Amazon using selenium", 1)
            return sTestStepReturnStatus

        else:
            CommonUtil.ExecLog(sModuleInfo, "Step return type unknown: %s" % (sTestStepReturnStatus), 3)
            temp_q.put("failed")
            CommonUtil.ExecLog(sModuleInfo, "Exit: Step - Add an item to cart on Amazon using selenium", 1)
            return sTestStepReturnStatus

    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info())