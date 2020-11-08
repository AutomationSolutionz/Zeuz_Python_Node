from Framework.Built_In_Automation.Sequential_Actions.sequential_actions import Sequential_Actions
from Framework.Utilities.All_Device_Info import get_all_connected_device_info
from Framework.Utilities.CommonUtil import parse_value_into_object
import json

if __name__ == "__main__":
    with open("TestCase.json", "r") as f:
        Test_Case2 = json.load(f)
    with open("TestCase.json", "w") as f:
        json.dump(Test_Case2, f, indent=2)

    step_data = []
    for i in Test_Case2["TestCases"][0]["Steps"]:
        all_actions = i["Step actions"]
        for j in all_actions:
            step_data.append(j["Action data"])

    final_dependency = Test_Case2["TestCases"][0]["final_dependency"]

    try:
        run_time_params = Test_Case2["TestCases"][0]["run_time_params"]
    except:
        run_time_params = {}

    device_info = get_all_connected_device_info()

    result = Sequential_Actions(
        step_data=step_data,
        _run_time_params=run_time_params,
        _dependency=final_dependency,
        debug_actions=None,
        _device_info=device_info
    )