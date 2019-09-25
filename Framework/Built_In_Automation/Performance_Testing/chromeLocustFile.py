from realbrowserlocusts import FirefoxLocust, ChromeLocust, PhantomJSLocust


from locust import TaskSet, task, HttpLocust
import time, ast, os, sys
sys.path.insert(0, os.getcwd())
from Framework import MainDriverApi
from Framework.Utilities import CommonUtil
from concurrent.futures import ThreadPoolExecutor

def get_stop_timeout():
    file = open(os.getcwd() + os.sep + 'Built_In_Automation' + os.sep + 'Performance_Testing' + os.sep +'locustFileInput.txt','r')
    stop_timeout=int(str(file.readline()).strip())
    return stop_timeout

class LocustUserBehavior(TaskSet):


    def runLocust(self):
        file = open(os.getcwd() + os.sep + 'Built_In_Automation' + os.sep + 'Performance_Testing' + os.sep +'locustFileInput.txt','r')
        file.readline()
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

    @task
    def runTestCase(self):
        self.runLocust()
        #self.client.timed_event_for_locust("Run", "Result", self.runLocust)

#class LocustUser(FirefoxLocust):
class LocustUser(ChromeLocust):
#class LocustUser(PhantomJSLocust):
#class LocustUser(HttpLocust):
    stop_timeout = get_stop_timeout() #in seconds in waitUntil thingies
    min_wait = 5000
    max_wait = 9000
    screen_width = 1200
    screen_height = 600
    locust_output_file_path = os.getcwd() + os.sep + 'Built_In_Automation' + os.sep + 'Performance_Testing' + os.sep + 'locustFileOutput.txt'
    if os.path.exists(locust_output_file_path):
        os.remove(locust_output_file_path)
        print "output file deleted"
    CommonUtil.log_thread_pool = ThreadPoolExecutor(max_workers=10)
    task_set = LocustUserBehavior