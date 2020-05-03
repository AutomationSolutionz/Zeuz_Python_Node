appium_driver = None

def set_appium_driver(driver):
    appium_driver = driver

def filter_optional_action_and_step_data(action):
    """
    Decorator for filtering actions for the following POINTS based on type of row
    1. ["platform", "optional parameter", "platform name - ios/android"]
        skips the action if the device platform and selected platform don't match
    2. ["propertyA | propertyB", "element parameter", "xyz"]
        returns the following modified data row
        ["propertyA", "element parameter", "xyz"] if android
        ["propertyB", "element parameter", "xyz"] if ios

    Tutorial for decorators: https://timber.io/blog/decorators-in-python/
    """

    import functools
    @functools.wraps(action)

    def decorated_action(data_set, *args, **kwargs):
        # This will be passed to the original function
        cleaned_data_set = []

        device_platform = appium_driver.capabilities['platformName'].strip().lower()

        for row in data_set:
            left, middle, right = row

            # POINT 1
            # Skip execution of action if the intended platform does not match with that of the device
            if "optional parameter" in middle and "platform" in left:
                if device_platform.strip().lower() == right.strip().lower():
                    # Skip this row, as its not intended to be a part of the actual step data
                    new_row = None
                else:
                    # Skip executing this action altogether if the intended platform does not match
                    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + action.__name__
                    CommonUtil.ExecLog(sModuleInfo,
                        "[SKIP] This action has been marked as optional and only intended for the platform '%s'" % right.strip(),
                        1)
                    return "passed"

            # POINT 2
            # If we find a '|' character in the left column, then try to check the platform
            # and filter the appropriate data for the left column by removing '|'
            if "element parameter" in middle and left.find("|") != -1:
                if device_platform == "android":
                    left = left.split("|")[0].strip()
                elif device_platform == "ios":
                    left = left.split("|")[1].strip()

            new_row = (left, middle, right,)

            if new_row:
                cleaned_data_set.append(new_row)

        return action(cleaned_data_set, *args, **kwargs)
    return decorated_action
