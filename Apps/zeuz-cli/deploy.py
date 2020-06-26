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
    headers['Content-Type'] = 'application/json'

    url = host + url

    response = requests.request(req_type, url, headers=headers, params=params, data=payload)
    return response


def get_available_machines(token, host, project, team):
    return req(
        "GET",
        host,
        "/api/machines/list",
        dict(),
        {
            "Authorization": "Bearer %s" % token
        },
        params={
            "project": project,
            "team": team,
            "user_level": "Automation"
        }
    ).json()


def get_run_status(token, host, run_id):
    return req(
        "GET",
        host,
        "/api/run/status",
        dict(),
        {
            "Authorization": "Bearer %s" % token
        },
        params={
            "run_id": run_id
        }
    ).json()


def get_test_set(token, host, project, team, test_set_name):
    return req(
        "GET",
        host,
        "/api/set/list",
        dict(),
        {
            "Authorization": "Bearer %s" % token
        },
        params={
            "project": project,
            "team": team,
            "search_term": test_set_name
        }
    ).json()


def get_milestone(token, host, project, team):
    return req(
        "GET",
        host,
        "/api/milestones/list",
        dict(),
        {
            "Authorization": "Bearer %s" % token
        },
        params={
            "project": project,
            "team": team,
            "status": "started"
        }
    ).json()


def deploy(token, host, payload_data):
    return req(
        "POST",
        host,
        "/api/run/submit",
        payload_data,
        {
            "Authorization": "Bearer %s" % token
        }
    ).json()


def get_token_from_api(api_key, host):
    return req(
        "GET",
        host,
        "/api/auth/token/verify",
        params={
            "api_key": api_key
        }
    ).json()


def main():
    # Error codes to return upon completion of main() function
    EXIT_CODE_SUCCESS = 0
    EXIT_CODE_ERR_NO_MACHINES = 1
    EXIT_CODE_ERR_INVALID_ARGS = 2
    EXIT_CODE_INVALID_API = 3
    EXIT_CODE_TEST_SET_NAME = 4
    EXIT_CODE_INVALID_MILESTONE = 5

    SLEEP_TIMEOUT = 30

    # Collect arguments from the command line
    try:
        parser = argparse.ArgumentParser(description="Zeuz CLI Tool")
        parser.add_argument("--host", help="Hostname of the server")
        parser.add_argument("--api_key", help="Your API key from Profile > API Key tab")
        parser.add_argument("--test_set_name", help="Name of the test set")
        parser.add_argument("--email", help="Email address where the report will be delivered")
        parser.add_argument("--objective", help="Objective of the deployment")
        parser.add_argument("--project", help="Project Id, example: PROJ-10")
        parser.add_argument("--team", help="Team Id, example: 10")
        parser.add_argument("--machine", help="Machine Id (default: any)")
        parser.add_argument("--milestone", help="Milestone Id")
        parser.add_argument("--machine_timeout", default=60, help="Minutes to wait for any automated machine to be available (default: 60)")
        parser.add_argument("--report_timeout", default=60, help="Minutes to wait before reporting the deployment progress [will be reported instantly upon completion] (default: 60)")

        args = parser.parse_args()

        host = args.host
        api_key = args.api_key
        test_set_name = args.test_set_name
        email = args.email
        objective = args.objective
        project = args.project
        team = args.team
        machine = args.machine
        milestone = args.milestone
        machine_timeout = int(args.machine_timeout)
        report_timeout = int(args.report_timeout)
    except:
        print("Provide all the arguments. Execute 'python deploy.py -h' to learn more")
        return EXIT_CODE_ERR_INVALID_ARGS


    # Get token for the given API key
    token = get_token_from_api(api_key, host)
    if "status" in token and token["status"] == 404:
        print("Invalid API key")
        return EXIT_CODE_INVALID_API
        
	
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
    if machine == "any":
        for _ in range(machine_timeout):
            machine_list = get_available_machines(token, host, project, team)
            if len(machine_list) == 0:
                time.sleep(SLEEP_TIMEOUT)
                machine_list = None
            else:
                machine = machine_list[0]["id"]
                break

    if machine_list == None:
        print("Could not find any available automated machine... exiting")
        return EXIT_CODE_ERR_NO_MACHINES

    payload_data = json.dumps({
        "test_set_name": test_set_name,
        "dependency": {
            "Brower": "Chrome",
            "OS": "Windows"
        },
        "email_receiver":[
            email,
        ],
        "objective": objective,
        "milestone": milestone,
        "project_id": project,
        "team_id": team,
        "run_time_params": {},
        "machine": machine,
        "loop": "1",
        "run_time_settings": {
            "threading": False,
            "take_screenshot": True,
            "debug_mode": False,
            "upload_log_file_only_for_fail": True
        },
        "branch_version":[],
        "start_date": str(datetime.datetime.now().date()),
        "end_date": str(datetime.datetime.now().date()),
        "domain": host
    })

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
    
    for _ in range(2 * report_timeout):
        run_status = get_run_status(token, host, deploy_info["run_id"])

        if run_status["run_id_status"].lower() in RUN_COMPLETE:
            print(run_status["run_id_status"].lower())
            break

        # Retry after 1 minute
        time.sleep(SLEEP_TIMEOUT)
    else:
        # Deployment still in progress
        print("in-progress")

    print(run_url)

    return EXIT_CODE_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
