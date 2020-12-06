import sys
from pathlib import Path
import traceback
sys.path.append(str(Path("../../")))

from Framework.Built_In_Automation.Sequential_Actions.sequential_actions import Sequential_Actions
from Framework.Utilities.All_Device_Info import get_all_connected_device_info
import json


def main(test_case_title=None):
    try:
        with open("TestCases.json", "r") as f:
            Test_Case = json.loads(f.read())

            step_data = []
            final_dependency = {}
            run_time_params = {}

            if len(Test_Case["TestCases"]) > 0:
                test_case = Test_Case["TestCases"][0]
            else:
                print("No test cases present in TestCases.json file.")
                return "failed"

            if test_case_title is not None:
                for cur_test_case in Test_Case["TestCases"]:
                    if cur_test_case["Title"] == test_case_title:
                        test_case = cur_test_case
                        break
                else:
                    print("Failed to find the test case with title %s" % test_case_title)
                    return "failed"

            # Gather data about all the steps
            for i in test_case["Steps"]:
                all_actions = i["Step actions"]
                for j in all_actions:
                    step_data.append(j["Action data"])

            # Gather dependency and other params
            try: final_dependency = test_case["dependency"]
            except: pass

            try: run_time_params = test_case["run_time_params"]
            except: pass

            device_info = get_all_connected_device_info()

            result = Sequential_Actions(
                step_data=step_data,
                _run_time_params=run_time_params,
                _dependency=final_dependency,
                debug_actions=None,
                _device_info=device_info
            )

            return result

    except:
        print("Failed to open TestCases.json file. Aborting.")
        traceback.print_exc()
        return "failed"


if __name__ == "__main__":
    main()
