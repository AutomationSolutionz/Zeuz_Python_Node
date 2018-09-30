import os
from appium import webdriver
import os.path


driver = ""
global driver


def setUp():
    # uncomment below if app is not installed
    try:
        app = os.path.join(os.path.dirname(__file__), 'FleetLogic.app')
        driver = webdriver.Remote(
            command_executor='http://127.0.0.1:4723/wd/hub',
            desired_capabilities={
                'app': app,
                'platformName': 'iOS',
                'platformVersion': '12.0',
                'deviceName': 'iPhone X',
                'bundleId': 'com.texadasoftware.fleetlogicdev'
            })
        return driver
    except Exception, e:
        print "not able to create driver", e

#ios_device_driver = setUp()