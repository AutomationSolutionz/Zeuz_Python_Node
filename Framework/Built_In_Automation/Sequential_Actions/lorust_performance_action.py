import inspect
import json
import time
import subprocess
import platform
from pathlib import Path
from typing import List, Tuple

from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
from Framework.Utilities import CommonUtil, ConfigModule


PROJECT_ROOT = Path.cwd().parent
AUTOMATION_LOG_DIR = PROJECT_ROOT / "AutomationLog"

MODULE_NAME = "lorust_performance_action"

def lorust_performance_action_handler(
    data_set: List[List[str]],
    step_data: List[List[List[str]]],
) -> Tuple[str, List[int]]:
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    actions_to_execute: List[int] = []
    teststarttime = time.perf_counter()
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

                try:
                    body = find_row_by(action, mid="body")[0]
                    body_type = body[0].strip()
                    if body_type == "Empty":
                        # 1. No body
                        #
                        # "Empty"
                        body = "Empty"
                    elif body[0].strip() == "Raw: json":
                        # This is a convenience (special) case for #2 mentioned below,
                        # for passing json data.
                        body = {
                            "Raw": json.dumps(CommonUtil.parse_value_into_object(body[2])),
                        }
                    else:
                        # 2. Raw string - mostly used with the "Content-Type" header having the values:
                        #       application/json
                        #       text/plain
                        # {
                        #     "Raw": "some raw string"
                        # }
                        #
                        # 3. Form data - both strings and files are supported, used with "Content-Type":
                        #       multipart/form-data
                        # {
                        #     "FormData": [
                        #         ["first_name", { "Str": "Mini" }],
                        #         ["last_name", { "Str": "Tiny" }],
                        #         ["age", { "Str": "10" }],
                        #         ["profile_picture_file", { "FilePath": "/path/to/profile/picture" }]
                        #     ]
                        # }
                        #
                        # 4. Form URL Encoded data, used with "Content-Type":
                        #       application/x-www-form-urlencoded
                        # {
                        #     "FormUrlEncoded": [
                        #         ["first_name", "Mini"],
                        #         ["last_name", "Tiny"],
                        #         ["age", 10]
                        #     ]
                        # }
                        #
                        # 5. Binary file upload, used with "Content-Type":
                        #       application/octet-stream
                        # {
                        #     "BinaryOctetFilePath": "/path/to/file"
                        # }
                        body = {
                            body[0]: body[2],
                        }
                except:
                    body = "Empty"

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
                duration = find_row_by(action, left="duration")[0][2]

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
            )) / run_id.replace(":", "-") / CommonUtil.current_session_name / CommonUtil.current_tc_no

        metrics_output_path = save_path / "lorust_performance_report"
        metrics_output_path.mkdir(parents=True, exist_ok=True)

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

        lorust_path = PROJECT_ROOT / "Apps" / "lorust"
        lorust_path.mkdir(parents=True, exist_ok=True)

        # Select the path based on os and arch since there will be separate
        # executables for each os. We may also download on demand.
        uname = platform.uname()

        # Example: lorust_Linux_x86_64.exe, lorust_Darwin_arm64.exe, lorust_Windows_x86_64.exe
        binary_name = f"lorust_{uname.system}_{uname.machine}.exe"
        lorust_path = lorust_path / binary_name

        subprocess.run(' '.join([
            str(lorust_path),
            f"--output-path {metrics_output_path}",
            f"--flow-path {flow_save_path}",
        ]), shell=True)

        testendtime = time.perf_counter()
        duration = testendtime - teststarttime

        CommonUtil.performance_testing = False
        CommonUtil.ExecLog(
            sModuleInfo,
            "DONE 'lorust'",
            1,
        )

        process_lorust_metrics(metrics_output_json_path)
        create_html_report(
            run_id=run_id, # type: ignore
            tc_id=CommonUtil.current_tc_no,
            report_save_path=metrics_output_path,
            teststarttime=teststarttime,
            testendtime=testendtime,
            duration=duration,
        )
    except:
        import traceback
        traceback.print_exc()

    # TODO: Return the performance data
    return "passed", actions_to_execute


def create_html_report(
    run_id: str,
    tc_id: str,
    report_save_path: Path,
    teststarttime: float,
    testendtime: float,
    duration: float,
):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME
    from jinja2 import Environment, FileSystemLoader

    processed_performance_data = CommonUtil.generate_time_based_performance_report(
        run_id=run_id,
        tc_id=tc_id,
        teststarttime=teststarttime,
        testendtime=testendtime,
        duration=duration,
        perf_data=CommonUtil.api_performance_data,
    )

    env = Environment(loader=FileSystemLoader('../reporting/html_templates'))
    template = env.get_template("lorust_perf_report.html")
    html = template.render(processed_performance_data)

    step_no: int = CommonUtil.current_step_sequence # type: ignore
    action_no: int = CommonUtil.current_action_no # type: ignore
    file_name = report_save_path / f"{tc_id}_STEP-{step_no}_ACTION-{action_no}.html"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(html)

    CommonUtil.ExecLog(
        sModuleInfo,
        "Lorust performance report generated successfully. "
        "Download the report from RunID > Test case > Download Logs.",
        1,
    )

    try: CommonUtil.processed_performance_data.clear()
    except: pass


def process_lorust_metrics(metrics_path):
    with open(metrics_path, "r") as f:
        data = json.loads(f.read())

        for point in data:
            performance_status = CommonUtil.PerformanceDataPoint(
                url= point["url"],
                http_verb= point["http_verb"],
                status_code= point["status_code"],
                response_body_size= point["response_body_size"],
                time_stamp= point["time_stamp"],
                response_body= point["response_body"],
                upload_total= point["upload_total"],
                download_total= point["download_total"],
                upload_speed= point["upload_speed"],
                download_speed= point["download_speed"],
                namelookup_time= point["namelookup_time"],
                connect_time= point["connect_time"],
                tls_handshake_time= point["tls_handshake_time"],
                starttransfer_time= point["starttransfer_time"],
                elapsed_time= point["elapsed_time"],
                redirect_time= point["redirect_time"],
            )
            CommonUtil.api_performance_data.append(performance_status)
