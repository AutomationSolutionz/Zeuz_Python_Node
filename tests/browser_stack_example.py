from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# desired_cap = {
#     # Set your access credentials
#     "browserstack.user": "oytizzo_OeMpca",
#     "browserstack.key": "iBCGGxGkwmC8p28wcgnV",
#
#     # Set URL of the application under test
#     "app": "bs://c700ce60cf13ae8ed97705a55b8e022f13c5827c",
#
#     # Specify device and os_version for testing
#     "device": "Google Pixel 3",
#     "os_version": "9.0",
#
#     # Set other BrowserStack capabilities
#     "project": "First Python project",
#     "build": "browserstack-build-1",
#     "name": "first_test"
# }
desired_cap = {}
desired_cap["browserstack.user"] = "oytizzo_OeMpca"
desired_cap["browserstack.key"] = "iBCGGxGkwmC8p28wcgnV"
desired_cap["app"] = "bs://c700ce60cf13ae8ed97705a55b8e022f13c5827c"
desired_cap["device"] = "Google Pixel 3"
desired_cap["os_version"] = "9.0"
desired_cap["project"] = "Project - appium v1"
desired_cap["build"] = "build-appium v1"
desired_cap["name"] = "TC - appium v1"


# Initialize the remote Webdriver using BrowserStack remote URL
# and desired capabilities defined above
driver = webdriver.Remote(
    # command_executor="http://localhost:4444/wd/hub/",
    command_executor="http://hub-cloud.browserstack.com/wd/hub",
    desired_capabilities=desired_cap
)

# Test case for the BrowserStack sample Android app.
# If you have uploaded your app, update the test case here.
search_element = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((MobileBy.ACCESSIBILITY_ID, "Search Wikipedia"))
)
search_element.click()
search_input = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((MobileBy.ID, "org.wikipedia.alpha:id/search_src_text"))
)
search_input.send_keys("BrowserStack")
time.sleep(5)
search_results = driver.find_elements_by_class_name("android.widget.TextView")
assert (len(search_results) > 0)
# Invoke driver.quit() after the test is done to indicate that the test is completed.
driver.quit()