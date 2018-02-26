import os, sys
import inspect
from Framework.Utilities import CommonUtil
from Projects.Sample_Facebook_Testing import Facebook

from Framework.Utilities.CommonUtil import passed_tag_list, failed_tag_list

def login_to_facebook_app(dependency,run_time_params,step_data,file_attachment,temp_q,screen_capture,device_info):
    try:
        sTestStepReturnStatus = Facebook.Login_to_Facebook(step_data)
        return CommonUtil.Result_Analyzer(sTestStepReturnStatus, temp_q)
    except Exception:
        return CommonUtil.Exception_Handler(sys.exc_info(), temp_q)
