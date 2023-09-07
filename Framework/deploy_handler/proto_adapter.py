# Auhtor: sazid

import json
from typing import Dict, List

# Uncomment the following lines for single-file debug
# import sys
# sys.path.append(str(Path.cwd() / "Framework" / "pb" / "v1"))
# from pb.v1.deploy_response_message_pb2 import DeployResponse

# Comment the following line for single-file debug
from Framework.pb.v1.deploy_response_message_pb2 import DeployResponse


def read_actions(actions_pb) -> List[Dict]:
    actions = []
    for action in actions_pb:
        rows = []
        actions.append({
            "action_name": action["name"],
            "action_disabled": not action["enabled"],
            "step_actions": rows,
        })

        for row in action.rows:
            rows.append([
                row["data"][0],
                row["data"][1],
                row["data"][2],
            ])
    return actions


def read_steps(steps_pb) -> List[Dict]:
    steps = []
    for step in steps_pb:
        attachments = []
        for attachment in step["stepInfo"]["attachments"]:
            attachments.append({
                "id": attachment["id"],
                "path": attachment["path"],
                "uploaded_by": attachment["uploadedBy"],
                "uploaded_at": attachment["uploadedAt"],
                "hash": attachment["hash"],
            })

        steps.append(
            {
                "step_id": step["stepId"], # TODO: verify if it should be step["id"] or step["stepId"]
                "step_name": step["name"],
                "step_sequence": step["sequence"],
                "step_driver_type": step["stepInfo"]["driver"],
                "automatablity": step["stepInfo"]["stepType"],
                "always_run": step["stepInfo"]["alwaysRun"],
                "run_on_fail": step["stepInfo"]["runOnFail"],
                "step_function": "Sequential Actions",
                "step_driver": step["stepInfo"]["driver"],
                "type": step["type"],
                "attachments": attachments,
                # "verify_point": step["stepInfo"]["verifyPoint"], //global verify_point ,step["verifyPoint"] // local verify point 
                "verify_point": step["verifyPoint"], 
                "continue_on_fail": step["continuePoint"],
                "step_time": step["time"],
                "actions": read_actions(step["actions"]),
            }
        )
    return steps


def read_test_cases(test_cases_pb) -> List[Dict]:
    test_cases = []
    for tc in test_cases_pb:
        attachments = []
        for attachment in tc["attachments"]:
            attachments.append({
                "id": attachment["id"],
                "path": attachment["path"],
                "uploaded_by": attachment["uploadedBy"],
                "uploaded_at": attachment["uploadedAt"],
                "hash": attachment["hash"],
            })

        test_cases.append({
            "testcase_no": tc["testCaseDetail"]["id"],
            "title": tc["testCaseDetail"]["name"],
            "automatability": tc["testCaseDetail"]["automatability"],
            "debug_steps": [],
            "attachments": attachments,
            "steps": read_steps(tc["steps"]),
        })
    return test_cases


def adapt(message: str, node_id: str) -> List[Dict]:
    """
    adapt takes the deploy_response and converts it to a python dictionary
    suitable for consumption by MainDriver.
    """

    r = json.loads(message)

    # TODO: Check r.server_version and create different adapeter classes for new
    # schemaa changes.

    result = {
        "server_version": r["serverVersion"],

        "run_id": r["runId"],
        "objective": r["deployInfo"]["objective"],
        "project_id": r["deployInfo"]["projectId"],
        "team_id": r["deployInfo"]["teamId"],

        "test_cases": read_test_cases(r["testCases"]),

        "dependency_list": {
            "Browser": r["deployInfo"]["dependency"]["browser"],
            "Mobile": r["deployInfo"]["dependency"]["mobile"],
        },

        "device_info": None,

        "run_time": {},
        "file_name": f"{node_id}_1",

        "runtime_settings": {
            "debug_mode": r["deployInfo"]["debug"]["debugMode"],
            "is_linked": r["deployInfo"]["runtimeSettings"]["isLinked"],
            "local_run": r["deployInfo"]["runtimeSettings"]["localRun"],
            "rerun_on_fail": r["deployInfo"]["runtimeSettings"]["rerunOnFail"],
            "take_screenshot": r["deployInfo"]["runtimeSettings"]["takeScreenshot"],
            "threading": r["deployInfo"]["runtimeSettings"]["threading"],
            "upload_log_file_only_for_fail": r["deployInfo"]["runtimeSettings"]["uploadLogFileOnlyForFail"],
            "window_size_x": r["deployInfo"]["runtimeSettings"]["windowSizeX"],
            "window_size_y": r["deployInfo"]["runtimeSettings"]["windowSizeY"],
        },

        "debug": "yes" if r["deployInfo"]["debug"]["debugMode"] else "no",
        "debug_clean": "YES" if r["deployInfo"]["debug"]["cleanup"] else "NO",
        "debug_step_actions": [],
        "debug_steps": [],
    }

    # if r["deployInfo"].device_info:
    #     if r["deployInfo"].device_info == "local_device":
    #         r["deployInfo"].device_info = "[[1, 1]]"
    # else:
    #     r["deployInfo"].device_info = "[[1, 1]]"
    if r["deployInfo"]["deviceInfo"].strip() == "" \
            or r["deployInfo"]["deviceInfo"].strip() == "local_device":
        # r["deployInfo"]["deviceInfo"] = json.dumps([])
        r["deployInfo"]["deviceInfo"] = json.dumps([[1, 1]])

    result["device_info"] = json.loads(r["deployInfo"]["deviceInfo"])


    # Add debug information
    for tc in r["deployInfo"].debug.test_cases:
        actions = []
        for step in tc.steps:
            result["debug_steps"].append(step.sequence)
            actions += list(step.actions)

        result["debug_step_actions"] = actions
        # For now, node supports debugging only a single test case, which is why
        # we're breaking early. But this can be easily improved to handle
        # multiple test case debug.
        break


    # Read runtime parameters
    for rp in r["deployInfo"]["runtimeParameters"]:
        result["run_time"][rp.key] = {
            "field": rp["key"],
            "subfield": rp["value"],
        }

    return [result,]


if __name__ == "__main__":
    node_id = "admin_node1"
    with open("test.pb", "rb") as f:
        message = f.read()
        adapted_data = adapt(message, node_id)
        print(adapted_data)
