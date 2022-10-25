# Auhtor: sazid

import json
from pathlib import Path
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
            "action_name": action.name,
            "action_disabled": not action.enabled,
            "step_actions": rows,
        })

        for row in action.rows:
            rows.append([
                row.data[0],
                row.data[1],
                row.data[2],
            ])
    return actions


def read_steps(steps_pb) -> List[Dict]:
    steps = []
    for step in steps_pb:
        attachments = []
        for attachment in step.step_info.attachments:
            attachments.append({
                "id": attachment.id,
                "path": attachment.path,
                "uploaded_by": attachment.uploaded_by,
                "uploaded_at": attachment.uploaded_at,
                "hash": attachment.hash,
            })

        steps.append(
            {
                "step_id": step.step_id, # TODO: verify if it should be step.id or step.step_id
                "step_name": step.name,
                "step_sequence": step.sequence,
                "step_driver_type": step.step_info.driver,
                "automatablity": step.step_info.step_type,
                "always_run": step.step_info.always_run,
                "run_on_fail": step.step_info.run_on_fail,
                "step_function": "Sequential Actions",
                "step_driver": step.step_info.driver,
                "type": step.type,
                "attachments": attachments,
                "verify_point": step.step_info.verify_point,
                "continue_on_fail": step.continue_point,
                "step_time": step.time,
                "actions": read_actions(step.actions),
            }
        )
    return steps


def read_test_cases(test_cases_pb) -> List[Dict]:
    test_cases = []
    for tc in test_cases_pb:
        attachments = []
        for attachment in tc.attachments:
            attachments.append({
                "id": attachment.id,
                "path": attachment.path,
                "uploaded_by": attachment.uploaded_by,
                "uploaded_at": attachment.uploaded_at,
                "hash": attachment.hash,
            })

        test_cases.append({
            "testcase_no": tc.test_case_detail.id,
            "title": tc.test_case_detail.name,
            "automatability": tc.test_case_detail.automatability,
            "debug_steps": [],
            "attachments": attachments,
            "steps": read_steps(tc.steps),
        })
    return test_cases


def adapt(message: str, node_id: str) -> List[Dict]:
    """
    adapt takes the deploy_response and converts it to a python dictionary
    suitable for consumption by MainDriver.
    """

    r = DeployResponse()
    r.ParseFromString(message)

    # TODO: Check r.server_version and create different adapeter classes for new
    # schemaa changes.

    result = {
        "server_version": r.server_version,

        "run_id": r.run_id,
        "objective": r.deploy_info.objective,
        "project_id": r.deploy_info.project_id,
        "team_id": r.deploy_info.team_id,

        "test_cases": read_test_cases(r.test_cases),

        "dependency_list": {
            "Browser": r.deploy_info.dependency.browser,
            "Mobile": r.deploy_info.dependency.mobile,
        },

        "device_info": {
            "browser_stack": {},
        },

        "run_time": {},
        "file_name": f"{node_id}_1",

        "runtime_settings": {
            "debug_mode": r.deploy_info.debug.debug_mode,
            "is_linked": r.deploy_info.runtime_settings.is_linked,
            "local_run": r.deploy_info.runtime_settings.local_run,
            "rerun_on_fail": r.deploy_info.runtime_settings.rerun_on_fail,
            "take_screenshot": r.deploy_info.runtime_settings.take_screenshot,
            "threading": r.deploy_info.runtime_settings.threading,
            "upload_log_file_only_for_fail": r.deploy_info.runtime_settings.upload_log_file_only_for_fail,
            "window_size_x": r.deploy_info.runtime_settings.window_size_x,
            "window_size_y": r.deploy_info.runtime_settings.window_size_y,
        },

        "debug": "yes" if r.deploy_info.debug.debug_mode else "no",
        "debug_clean": "YES" if r.deploy_info.debug.cleanup else "NO",
        "debug_step_actions": [],
        "debug_steps": [],
    }

    if r.deploy_info.device_info:
        if r.deploy_info.device_info == "local_device":
            r.deploy_info.device_info = "[[1, 1]]"
    else:
        r.deploy_info.device_info = "[[1, 1]]"
    try:
        result["device_info"] = json.loads(r.deploy_info.device_info)
    except:
        result["device_info"] = str(r.deploy_info.device_info)


    # Add debug information
    for tc in r.deploy_info.debug.test_cases:
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
    for rp in r.deploy_info.runtime_parameters:
        result["run_time"][rp.key] = {
            "field": rp.key,
            "subfield": rp.value,
        }

    return [result,]


if __name__ == "__main__":
    node_id = "admin_node1"
    with open("test.pb", "rb") as f:
        message = f.read()
        adapted_data = adapt(message, node_id)
        print(adapted_data)
