from realbrowserlocusts import FirefoxLocust, ChromeLocust, PhantomJSLocust
from Framework.Built_In_Automation.Sequential_Actions import sequential_actions

from locust import TaskSet, task


class LocustUserBehavior(TaskSet):
    def runLocust(self):
        sequential_actions.Run_Sequential_Actions([])


#class LocustUser(FirefoxLocust):
class LocustUser(ChromeLocust):
#class LocustUser(PhantomJSLocust):
    timeout = 300 #in seconds in waitUntil thingies
    min_wait = 100
    max_wait = 1000
    screen_width = 1200
    screen_height = 600
    task_set = LocustUserBehavior