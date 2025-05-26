import sys
from pathlib import Path
import traceback
sys.path.append(str(Path("../../")))

from Framework.Utilities import ConfigModule
from Framework import MainDriverApi
from Framework.Utilities.All_Device_Info import get_all_connected_device_info
import json, os
top_path = os.path.dirname(os.getcwd())
drivers_path = os.path.join(top_path, "Drivers")
sys.path.append(drivers_path)


def main():
    try:
        with open("TestCases.json", "r") as f:
            Json_data = json.load(f)
            if isinstance(Json_data, str):
                Json_data = json.loads(Json_data)
        with open("TestCases.json", "w") as f:
            json.dump(Json_data, f, indent=2)
    except:
        print("Failed to open TestCases.json file. Aborting.")
        traceback.print_exc()
        return "zeuz_failed"

    try:
        ConfigModule.remote_config["local_run"] = True
        ConfigModule.remote_config["threading"] = False
        ConfigModule.remote_config["take_screenshot"] = False
        if len(Json_data["TestCases"]) > 0:
            pass
        else:
            print("No test cases present in TestCases.json file.")
            return "zeuz_failed"

        local_run_dataset = {}
        Set_dataset = []
        TestCaseLists = []
        Set_meta_data = []
        all_test_case_detail = []
        all_debug_steps = ["DN11", "DN11"]
        all_file_specific_steps = [{}, {}]
        all_test_case_result_index = ["DN12", "DN12"]
        all_TestStepsList = []

        # Gather data about all the test cases
        i = 0
        for test_case in Json_data["TestCases"]:
            TestCaseLists.append(["TESTCASE %s" % (i+1), "automated", i + 1])
            all_test_case_detail.append([['DN08', test_case["Title"], 'DN09', 'DN10']])
            all_TestStepsList.append([])
            Set_dataset.append([])
            Set_meta_data.append([])
            j = 0
            for step in test_case["Steps"]:
                Set_dataset[i].append([])
                Set_meta_data[i].append([["DN06", False, 59]])
                all_TestStepsList[i].append([6279, step["Step name"], 1, 'Built_In_Driver', 'automated', False, True, 'Sequential Actions', 'Built_In_Driver', False])
                k = 0
                for action in step["Step actions"]:
                    Set_dataset[i][j].append([])
                    for row in action["Action data"]:
                        Set_dataset[i][j][k].append(row)
                    k += 1
                j += 1
            i += 1

        local_run_dataset["final_dependency"] = Json_data["TestCases"][0]["dependency"] if "dependency" in Json_data["TestCases"][0] else {}
        local_run_dataset["final_run_params"] = Json_data["TestCases"][0]["run_time_params"] if "run_time_params" in Json_data["TestCases"][0] else {}
        local_run_dataset["Set_dataset"] = Set_dataset
        local_run_dataset["TestCaseLists"] = TestCaseLists
        local_run_dataset["Set_meta_data"] = Set_meta_data
        local_run_dataset["all_test_case_detail"] = all_test_case_detail

        local_run_dataset["all_file_specific_steps"] = all_file_specific_steps
        local_run_dataset["all_test_case_result_index"] = all_test_case_result_index
        local_run_dataset["all_TestStepsList"] = all_TestStepsList

        user_info_object = {"project": "DN", "team": "DN"}

        device_info = get_all_connected_device_info()
        result = MainDriverApi.main(
            device_dict=device_info,
            user_info_object=user_info_object,
            local_run_dataset=local_run_dataset
        )

        return result
    except:
        print("Could not perform local run")
        traceback.print_exc()
        return "zeuz_failed"


if __name__ == "__main__":
    main()
