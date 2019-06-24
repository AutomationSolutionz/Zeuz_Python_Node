from realbrowserlocusts import FirefoxLocust, ChromeLocust, PhantomJSLocust


from locust import TaskSet, task, HttpLocust
import time, ast, os, sys
#for testing, will change it
sys.path.insert(0, r'/home/batman/Desktop/Node_Latest_Sreejoy/ZeuzPythonNode/Framework')
from Framework import MainDriverApi

class LocustUserBehavior(TaskSet):


    def runLocust(self):
        print "Hello"
        #for testing, will change it
        file = open(r'/home/batman/Desktop/Node_Latest_Sreejoy/ZeuzPythonNode/Framework/Built_In_Automation/Performance_Testing/locustFileInput.txt','r')
        TestCaseID=str(file.readline()).strip()
        print TestCaseID
        sModuleInfo=str(file.readline()).strip()
        print sModuleInfo
        run_id=str(file.readline()).strip()
        print run_id
        driver_list=ast.literal_eval(str(file.readline()).strip())
        print driver_list
        final_dependency=ast.literal_eval(str(file.readline()).strip())
        print final_dependency
        final_run_params=ast.literal_eval(str(file.readline()).strip())
        print final_run_params
        temp_ini_file=str(file.readline()).strip()
        print temp_ini_file
        is_linked=str(file.readline()).strip()
        print is_linked
        send_log_file_only_for_fail=ast.literal_eval(str(file.readline()).strip())
        print send_log_file_only_for_fail
        file.close()
        MainDriverApi.run_test_case(TestCaseID, sModuleInfo, run_id, driver_list, final_dependency, final_run_params, temp_ini_file, is_linked, send_log_file_only_for_fail, True, self.client)

    @task(1)
    def runTestCase(self):
        self.client.timed_event_for_locust("Run", "Result", self.runLocust)

#class LocustUser(FirefoxLocust):
class LocustUser(ChromeLocust):
#class LocustUser(PhantomJSLocust):
#class LocustUser(HttpLocust):
    timeout = 100 #in seconds in waitUntil thingies
    min_wait = 5000
    max_wait = 9000
    screen_width = 1200
    screen_height = 600
    value=10
    #LocustUserBehavior.val=value
    task_set = LocustUserBehavior