import sys
import os
sys.path.append("..")

from Utilities import CommonUtil


#local_run = True
local_run = False

class AuthorizationData:

    def __init__(self,
                 account_id=None,
                 customer_id=None,
                 developer_token=None,
                 authentication=None):

        self._account_id = account_id
        self._customer_id = customer_id
        self._developer_token = developer_token
        self._authentication = authentication

    @property
    def account_id(self):
        return self._account_id

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def developer_token(self):
        return self._developer_token

    @property
    def authentication(self):
        return self._authentication

    @account_id.setter
    def account_id(self, account_id):
        self._account_id = account_id

    @customer_id.setter
    def customer_id(self, customer_id):
        self._customer_id = customer_id

    @developer_token.setter
    def developer_token(self, developer_token):
        self._developer_token = developer_token

    @authentication.setter
    def authentication(self, authentication):
        self._authentication = authentication

def Exception_Info(sModuleInfo, errMsg):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
    CommonUtil.ExecLog(sModuleInfo, errMsg + ".  Error: %s"%(Error_Detail), 3,local_run)
    return "failed"
