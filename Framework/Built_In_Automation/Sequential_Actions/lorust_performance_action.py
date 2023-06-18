import inspect
import json
import subprocess
import platform
from pathlib import Path
from typing import Callable, List, Tuple, Any

from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
from Framework.Utilities import CommonUtil, ConfigModule


PROJECT_ROOT = Path.cwd().parent
AUTOMATION_LOG_DIR = PROJECT_ROOT / "AutomationLog"

MODULE_NAME = "lorust_performance_action"

def lorust_performance_action_handler(
    data_set: List[List[str]],
    run_sequential_actions: Callable[[List[int]], Tuple[str, List[int]]],
    timestamp_func: Callable[[], str],
    step_data: List[List[List[str]]],
) -> Tuple[str, List[int], List[Any]]:
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    actions_to_execute: List[int] = []
    try:
        spawn_rate = "1"
        max_tasks = None
        timeout = 1

        for left, _, right in data_set:
            left, right = left.strip(), right.strip()
            if "spawn rate" in left:
                if right.strip().startswith("%|"):
                    spawn_rate = sr.get_previous_response_variables_in_strings(right.strip()) # type: ignore
                else:
                    spawn_rate = right
            elif "max tasks" in left:
                if right.strip().startswith("%|"):
                    max_tasks = int(sr.get_previous_response_variables_in_strings(right.strip())) # type: ignore
                else:
                    max_tasks = int(right)
            elif "timeout" in left:
                if right.strip().startswith("%|"):
                    timeout = int(sr.get_previous_response_variables_in_strings(right.strip())) # type: ignore
                else:
                    timeout = int(right)
            elif "lorust performance action" in left:
                if right.strip().startswith("%|"):
                    right = sr.get_previous_response_variables_in_strings(right.strip()) # type: ignore

                action_ranges = right.split(',')

                actions_to_execute=[]
                for action_range in action_ranges:
                    action_range=action_range.split('-') #[5-7] to [5,7], [5] to [5] if no '-' present
                    if len(action_range) == 1:
                        actions_to_execute.append(int(action_range[0].strip())-1)
                    else:
                        l, r = map(int, action_range) #[9,14] to l=9 and r=14
                        for i in range(l, r+1):
                            actions_to_execute.append(i-1) #[9,10,11,12,13,14]

        def find_row_by(
                action: List[List[str]],
                left: str | None = None,
                mid: str | None = None,
                right: str | None = None,
        ) -> List[List[str]]:
            result: List[List[str]] = []
            for _left, _mid, _right in action:
                if left and _left.strip() == left.strip():
                    result.append([_left, _mid, _right])
                elif mid and _mid.strip() == mid.strip():
                    result.append([_left, _mid, _right])
                elif right and _right.strip() == right.strip():
                    result.append([_left, _mid, _right])
            return result

        # Datasets of actions to be executed under this load generator session.
        load_action_datasets = []
        for i in actions_to_execute:
            load_action_datasets.append(step_data[i])

        # Construct the json config (flow) for lorust load generator
        load_gen_function = {
            "spawn_rate": spawn_rate,
            "timeout": timeout,
            "functions_to_execute": []
        }
        flow = {
            "functions": [
                {
                    "LoadGen": load_gen_function,
                }
            ]
        }

        for action in load_action_datasets:
            action_name = action[-1][0].strip()
            function = {}

            if action_name == "lorust::HttpRequest":
                url = find_row_by(action, "url")[0][2]

                try: method = find_row_by(action, left="method")[0][2]
                except: method = "GET"

                try: body = find_row_by(action, mid="body")[0][2]
                except: body = "Empty"

                try: redirect_limit = int(find_row_by(action, left="redirect_limit")[0][2])
                except: redirect_limit = None

                try: timeout = int(find_row_by(action, left="timeout")[0][2])
                except: timeout = None

                header_rows = find_row_by(action, mid="headers")
                headers: List[List[str]] = []
                for row in header_rows:
                    headers.append([row[0], row[2]])

                function = {
                    "HttpRequest": {
                        "method": method,
                        "url": url,
                        "headers": headers,
                        "body": body,
                        "redirect_limit": redirect_limit,
                        "timeout": timeout,
                    },
                }

            elif action_name == "lorust::Sleep":
                duration = int(find_row_by(action, left="duration")[0][2])

                function = {
                    "Sleep": {
                        "duration": duration,
                    },
                }

            elif action_name == "lorust::RunRhaiCode":
                code = find_row_by(action, left="code")[0][2]

                function = {
                    "RunRhaiCode": {
                        "code": code,
                    },
                }

            load_gen_function["functions_to_execute"].append(function)

        run_id = sr.Get_Shared_Variables("run_id")
        temp_ini_file = AUTOMATION_LOG_DIR / ConfigModule.get_config_value("Advanced Options", "_file")
        save_path = Path(ConfigModule.get_config_value(
                "sectionOne",
                "temp_run_file_path",
                temp_ini_file,
            )) / run_id.replace(":", "-") / CommonUtil.current_session_name

        metrics_output_path = save_path / "metrics"
        metrics_output_path.mkdir(parents=True)

        flow_save_path = metrics_output_path / "flow.json"
        metrics_output_json_path = metrics_output_path / "http.json"

        # Save the flow configuration
        with open(flow_save_path, "w") as f:
            f.write(json.dumps(flow))

        CommonUtil.ExecLog(
            sModuleInfo,
            "LAUNCHING 'lorust'...",
            1,
        )

        # TODO: Select the path based on os and arch since there
        # will be separate executables for each os. We may also
        # download on demand.
        uname = platform.uname()

        # Example: lorust_Linux_x86_64, lorust_Darwin_arm64
        binary_name = f"lorust_{uname.system}_{uname.machine}"
        lorust_path = PROJECT_ROOT / "Apps" / "lorust" / binary_name

        subprocess.run(' '.join([
            str(lorust_path),
            f"--output-path {metrics_output_path}",
            f"--flow-path {flow_save_path}",
        ]), shell=True)

        CommonUtil.performance_testing = False
        CommonUtil.ExecLog(
            sModuleInfo,
            "DONE 'lorust'",
            1,
        )
    except:
        import traceback
        traceback.print_exc()

    # TODO: Return the performance data
    return "passed", actions_to_execute, []
