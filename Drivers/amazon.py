import os, sys
import inspect
from Utilities import CommonUtil
from Projects.Sample_Amazon_Testing import Amazon

passed_tag_list=['Pass','pass','PASS','PASSED','Passed','passed','true','TRUE','True',True,1,'1','Success','success','SUCCESS']
failed_tag_list=['Fail','fail','FAIL','Failed','failed','FAILED','false','False','FALSE',False,0,'0']


def search_an_item_on_amazon(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
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


    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to search item: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"


def add_an_item_to_cart_on_amazon(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
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


    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to add item to cart: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"

def add_an_item_to_cart_on_amazon_using_selenium(dependency,run_time_params,step_data,file_attachment,temp_q):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
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

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to add item to cart: Error:%s" %( Error_Detail), 3)
        temp_q.put("Failed")
        return "failed"