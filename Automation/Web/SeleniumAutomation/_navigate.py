__author__ = 'shetu'
import sys
import os
import inspect
from selenium import webdriver
from Automation.Web.SeleniumAutomation import config as config
from Automation.Web.SeleniumAutomation._locateInteraction import Locate_Element_By_Tag
from Automation.Web.SeleniumAutomation import _textInteraction as t
from Automation.Web.SeleniumAutomation import _clickInteraction as c
def selectBrowser(browser):
    try:
        config.sBrowser.close()
    except:
        True
    try:
        browser = browser.lower()

        if browser == "chrome":
            config.__dict__['sBrowser'] = webdriver.Chrome()

        elif browser == 'firefox':
            config.__dict__['sBrowser'] = webdriver.Firefox()
        elif "ie" in browser:
            config.__dict__['sBrowser'] = webdriver.Ie()
        elif "safari" in browser:
            os.environ["SELENIUM_SERVER_JAR"] = os.sys.prefix + os.sep + "Scripts" + os.sep + "selenium-server-standalone-2.45.0.jar"
            config.__dict__['sBrowser'] = webdriver.Safari()
        else:
            print "Unable to start browser"
        if config.sBrowser:
            config.sBrowser.implicitly_wait(config.WebDriver_Wait_Short)
            config.sBrowser.maximize_window()
            return "passed"
        else:
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail

def openLink(web_link):
    try:
        config.sBrowser.get(web_link)
        print config.sBrowser.current_url
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        return "failed"

def tearDown():
    try:
        config.sBrowser.quit()
        return "passed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        return "failed"


def dataRetrieval(tag_name,index_list,parent=False):
    try:
        if index_list:
            element_list=Locate_Element_By_Tag(tag_name,parent,True)
        else:
            element_list=Locate_Element_By_Tag(tag_name,parent)
        if index_list:
            t=[]
            for i in element_list:
                #needs to be changed
                child=i.find_elements_by_xpath('.//*')
                m=[]
                for each in index_list:
                    m.append(child[each-1].text)
                t.append(tuple(m))
            return t
        else:
            return element_list.text
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        print "%s"%Error_Detail
        
        
def Login(user_name,password,logged_name):
    sModuleInfo = inspect.stack()[0][3] + " : " + inspect.getmoduleinfo(__file__).name
    try:
        t.Set_Text_By_ID("username",user_name)
        t.Set_Text_By_ID("password",password)
        c.Click_Element_By_ID("submit")
        element_login = WebDriverWait(sBrowser, WebDriver_Wait).until(EC.presence_of_element_located((By.XPATH, "//*[@title='View profile']")))
        if (WebDriverWait(element_login, WebDriver_Wait).until(lambda driver : element_login.text)) == logged_name:
            CommonUtil.ExecLog(sModuleInfo, "Verified that logged in as: %s"%logged_name, 1,local_run)
            return "passed"
        else:
            CommonUtil.ExecLog(sModuleInfo, "Log in failed for user: %s"%logged_name, 3,local_run)
            return "failed"
    except Exception, e:
        exc_type, exc_obj, exc_tb = sys.exc_info()        
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Error_Detail = ((str(exc_type).replace("type ", "Error Type: ")) + ";" +  "Error Message: " + str(exc_obj) +";" + "File Name: " + fname + ";" + "Line: "+ str(exc_tb.tb_lineno))
        CommonUtil.ExecLog(sModuleInfo, "Unable to login.  %s"%Error_Detail, 3,local_run)
        return "failed"
