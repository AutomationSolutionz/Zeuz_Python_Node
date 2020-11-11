#!/bin/python3
import sys
import json
import requests
import argparse
import time
import datetime


#############################################################
# Zeuz API Documentation                                    #
# https://documenter.getpostman.com/view/10815312/SzfAzSWj  #
#############################################################


def req(req_type, host, url, payload=dict(), headers=dict(), params=dict()):
    headers["Content-Type"] = "application/json"

    url = host + url

    response = requests.request(
        req_type,
        url,
        headers=headers,
        params=params,
        data=payload,
        verify=False
    )
    return response


def get_available_machines(token, host, project, team):
    return req(
        "GET",
        host,
        "/api/machines/list",
        dict(),
        {"Authorization": "Bearer %s" % token},
        params={"project": project, "team": team, "user_level": "Automation"},
    ).json()


def get_run_status(token, host, run_id):
    return req(
        "GET",
        host,
        "/api/run/status",
        dict(),
        {"Authorization": "Bearer %s" % token},
        params={"run_id": run_id},
    ).json()


def get_test_set(token, host, project, team, test_set_name):
    return req(
        "GET",
        host,
        "/api/set/list",
        dict(),
        {"Authorization": "Bearer %s" % token},
        params={"project": project, "team": team, "search_term": test_set_name},
    ).json()


def get_milestone(token, host, project, team):
    return req(
        "GET",
        host,
        "/api/milestones/list",
        dict(),
        {"Authorization": "Bearer %s" % token},
        params={"project": project, "team": team, "status": "started"},
    ).json()


def deploy(token, host, payload_data):
    return req(
        "POST",
        host,
        "/api/run/submit",
        payload_data,
        {"Authorization": "Bearer %s" % token},
    ).json()


def get_user_info(token, host):
    return req(
        "GET",
        host,
        "/api/user",
        dict(),
        {"Authorization": "Bearer %s" % token},
    ).json()[0]


def get_ondemand_node(token, host, user_id, username):
    return req(
        "GET",
        host,
        "/Home/ManageMachine/on_demand_node",
        dict(),
        dict(),
        params={"user_id": user_id, "username": username, "host": host},
    ).json()


def get_token_from_api(api_key, host):
    return req(
        "GET", host, "/api/auth/token/verify", params={"api_key": api_key}
    ).json()


def extract_runtime_parameters(param_str: str):
    """Extracts the JSON from the given string or file path and converts it
      into suitable a data object.

    Args:
        param_str: Either a file path containing a JSON string
          or a plain JSON string.

    Returns:
        A dictionary of the following format:

          {
              "key1": {
                  "field": "key1",
                  "subfield": "value1"
              },
              "key2": {
                  "field": "key2",
                  "subfield": "value2"
              },
              ...
          }
    """

    try:
        json_str = param_str

        # Try to see if the given argument is a file, open it
        try:
            with open(param_str, "r") as f:
                json_str = f.read()
        except:
            pass

        data = json.loads(json_str)
        result = {}

        for key in data:
            result[key] = {"field": key, "subfield": data[key]}

        return result
    except Exception as e:
        return None


def extract_dependencies(param_str: str):
    try:
        data = json.loads(param_str)
        return data
    except Exception as e:
        return {
            "Browser": "chromeheadless",
            "OS": "linux"
        }


def main():
    # Error codes to return upon completion of main() function
    EXIT_CODE_SUCCESS = 0
    EXIT_CODE_ERR_NO_MACHINES = 1
    EXIT_CODE_ERR_INVALID_ARGS = 2
    EXIT_CODE_INVALID_API = 3
    EXIT_CODE_TEST_SET_NAME = 4
    EXIT_CODE_INVALID_MILESTONE = 5
    EXIT_CODE_INVALID_RUNTIME_PARAMETERS = 6
    EXIT_CODE_FAILED_TO_CREATE_ONDEMAND_NODE = 7

    SLEEP_TIMEOUT = 30

    # Disable SSL warnings.
    requests.packages.urllib3.disable_warnings()

    # Collect arguments from the command line
    try:
        parser = argparse.ArgumentParser(description="Zeuz CLI Tool")
        parser.add_argument("--host", help="Hostname of the server")
        parser.add_argument("--api_key", help="Your API key from Profile > API Key tab")
        parser.add_argument("--test_set_name", help="Name of the test set")
        parser.add_argument(
            "--email", help="Email address where the report will be delivered"
        )
        parser.add_argument(
            "--email_pref",
            default="always",
            help="Email preference after deployment is complete. example: onfail/always (default: always)",
        )
        parser.add_argument("--objective", help="Objective of the deployment")
        parser.add_argument("--project", help="Project ID, example: PROJ-10")
        parser.add_argument("--team", help="Team ID, example: 10")
        parser.add_argument("--machine", help="Machine ID (default: any)")
        parser.add_argument("--milestone", help="Milestone ID")
        parser.add_argument(
            "--machine_timeout",
            default=60,
            help="Minutes to wait for any automated machine to be available (default: 60)",
        )
        parser.add_argument(
            "--report_timeout",
            default=60,
            help="Minutes to wait before reporting the deployment progress [will be reported instantly upon completion] (default: 60)",
        )
        parser.add_argument(
            "--runtime_parameters",
            help="Runtime parameters (must be in JSON format or a file containing JSON).",
        )
        parser.add_argument(
            "--dependency",
            default='{"Browser": "chromeheadless", "OS": "linux"}'
            help="Dependencies (must be in JSON format or a file containing JSON).",
        )
        parser.add_argument(
            "--report_filename",
            help="File path to save the detailed report. (default: report.json)",
        )

        args = parser.parse_args()

        host = args.host
        api_key = args.api_key
        test_set_name = args.test_set_name
        email = args.email
        email_pref = args.email_pref
        objective = args.objective
        project = args.project
        team = args.team
        machine = args.machine
        milestone = args.milestone
        runtime_parameters = args.runtime_parameters
        dependency = args.dependency
        machine_timeout = int(args.machine_timeout)
        report_timeout = int(args.report_timeout)
        report_filename = args.report_filename
    except:
        print("Provide all the arguments. Execute 'python deploy.py -h' to learn more")
        return EXIT_CODE_ERR_INVALID_ARGS

    if runtime_parameters:
        # Extract the runtime parameters from file or string into a python object
        runtime_parameters = extract_runtime_parameters(runtime_parameters)

        if not runtime_parameters:
            print("Invalid runtime parameters format/file.")
            return EXIT_CODE_INVALID_RUNTIME_PARAMETERS
    else:
        runtime_parameters = {}

    dependency = extract_dependencies(dependency)

    # Parse emails
    emails = [e.strip() for e in email.split(",")]

    # Get token for the given API key
    token = get_token_from_api(api_key, host)
    if "status" in token and token["status"] == 404:
        print("Invalid API key")
        return EXIT_CODE_INVALID_API

    # Extract token from request
    token = token["token"]

    # Verify test set
    r = get_test_set(token, host, project, team, test_set_name)
    if len(r) == 0:
        print("Invalid test set name")
        return EXIT_CODE_TEST_SET_NAME

    # Verify milestone
    milestone_started = False
    r = get_milestone(token, host, project, team)
    for info in r:
        if info["id"] == int(milestone):
            milestone_started = True
            break

    if not milestone_started:
        print("Invalid milestone (either not 'started' or invalid name)")
        return EXIT_CODE_INVALID_MILESTONE

    # If 'any' is specified as the parameter for machine,
    machine_list = list()
    machine_name = machine

    # If `ondemand` node needs to be created, create a new ondemand node
    # and select it.
    try:
        if machine_name == "ondemand":
            user_info = get_user_info(token, host)
            username = user_info["username"]
            user_id = user_info["uid"]

            ondemand_node = get_ondemand_node(token, host, user_id, username)

            # Wait 5 secs to let the on demand node start up properly.
            time.sleep(5)

            machine_name = ondemand_node["node_id"]
    except:
        return EXIT_CODE_FAILED_TO_CREATE_ONDEMAND_NODE

    for _ in range(machine_timeout):
        machine_list = get_available_machines(token, host, project, team)
        if len(machine_list) == 0:
            time.sleep(SLEEP_TIMEOUT)
        else:
            if machine_name == "any":
                machine = machine_list[0]["id"]
            else:
                machine = next(
                    (m["id"] for m in machine_list if m["name"] == machine_name),
                    None
                )
            break

    if len(machine_list) == 0 or machine is None:
        print("Could not find any available automated machine... exiting")
        return EXIT_CODE_ERR_NO_MACHINES

    payload_data = json.dumps(
        {
            "test_set_name": test_set_name,
            "dependency": dependency,
            "email_receiver": emails,
            "email_pref": email_pref,
            "objective": objective,
            "milestone": milestone,
            "project_id": project,
            "team_id": team,
            "run_time_params": runtime_parameters,
            "machine": machine,
            "loop": "1",
            "run_time_settings": {
                "threading": False,
                "take_screenshot": True,
                "debug_mode": False,
                "upload_log_file_only_for_fail": True,
            },
            "branch_version": [],
            "start_date": str(datetime.datetime.now().date()),
            "end_date": str(datetime.datetime.now().date()),
            "domain": host,
        }
    )

    deploy_info = None
    for _ in range(2 * machine_timeout):
        # Deploy the test set
        deploy_info = deploy(token, host, payload_data)

        if "status" in deploy_info and deploy_info["status"] == 400:
            time.sleep(SLEEP_TIMEOUT)
            deploy_info = None
        else:
            break

    if deploy_info == None:
        print("The specified machine is not available")
        return EXIT_CODE_ERR_NO_MACHINES

    run_url = host + "/Home/RunID/" + deploy_info["run_id"]

    # Status for complete runs
    RUN_COMPLETE = ["complete", "cancelled"]

    run_id_status = None
    report = None

    for _ in range(2 * report_timeout):
        run_status = get_run_status(token, host, deploy_info["run_id"])
        run_id_status = run_status["run_id_status"].lower()

        if run_id_status in RUN_COMPLETE:
            report = run_status
            break

        # Retry after 1 minute
        time.sleep(SLEEP_TIMEOUT)

    if run_id_status not in [RUN_COMPLETE]:
        # Deployment still in progress
        run_id_status = "in-progress"

    # Write brief report to console.
    print("STATUS", run_id_status)

    for key in report["status"]:
        print(key.upper(), report["status"][key])

    print("REPORT_URL", run_url)

    # Write detailed report to file.
    with open(report_filename, "w") as f:
        f.write(json.dumps(report))

    print("REPORT_FILE", report_filename)

    return EXIT_CODE_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
