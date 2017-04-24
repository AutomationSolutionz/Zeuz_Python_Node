
import os,sys,time
import inspect
from Framework.Utilities import CommonUtil, FileUtilities  as FL
local_run = False

Passed = "Passed"
Failed = "Failed"

def remove_a_desktop_folder(step_data):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name

    try:
        if ((len(step_data) != 1) or (1 < len(step_data[0]) >= 5)):
            CommonUtil.ExecLog(sModuleInfo,"The information in the data-set(s) are incorrect. Please provide accurate data set(s) information.",3)
            return "failed"
        else:
            file_location = FL.get_home_folder() + step_data[0][0][2]
            result = CommonUtil.run_cmd('rm -rf ' + file_location)
            CommonUtil.ExecLog(sModuleInfo, "Trying to delete folder: %s" % file_location, 1)
            return result

    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        error_detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" + "Error Message: " + str(exc_obj) +
                    ";" + "File Name: " + fname + ";" + "Line: " + str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to delete folder. Error: %s" % error_detail, 3)
        return Failed
