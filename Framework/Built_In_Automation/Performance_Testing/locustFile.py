#from realbrowserlocusts import FirefoxLocust, ChromeLocust, PhantomJSLocust


from locust import TaskSet, task, HttpLocust
import time, ast, os, sys
#for testing, will change it
sys.path.insert(0, r'/home/batman/Desktop/Node_Latest_Sreejoy/ZeuzPythonNode/Framework')
from Framework import MainDriverApi

class LocustUserBehavior(TaskSet):

    @task
    def runLocust(self):
        print "Hello"
        #for testing, will change it
        file = open(r'/home/batman/Desktop/Node_Latest_Sreejoy/ZeuzPythonNode/Framework/Built_In_Automation/Performance_Testing/locustFileInput.txt','r')
        TestCaseID=file.readline()
        print TestCaseID
        sModuleInfo=file.readline()
        print sModuleInfo
        run_id=file.readline()
        print run_id
        driver_list=ast.literal_eval(file.readline())
        print driver_list
        final_dependency=ast.literal_eval(file.readline())
        print final_dependency
        final_run_params=ast.literal_eval(file.readline())
        print final_run_params
        temp_ini_file=file.readline()
        print temp_ini_file
        is_linked=file.readline()
        print is_linked
        send_log_file_only_for_fail=ast.literal_eval(file.readline())
        print send_log_file_only_for_fail
        file.close()
        MainDriverApi.run_test_case(TestCaseID, sModuleInfo, run_id, driver_list, final_dependency, final_run_params, temp_ini_file, is_linked, send_log_file_only_for_fail)


#class LocustUser(FirefoxLocust):
#class LocustUser(ChromeLocust):
#class LocustUser(PhantomJSLocust):
class LocustUser(HttpLocust):
    timeout = 300 #in seconds in waitUntil thingies
    min_wait = 100
    max_wait = 1000
    screen_width = 1200
    screen_height = 600
    value=10
    #LocustUserBehavior.val=value
    task_set = LocustUserBehavior