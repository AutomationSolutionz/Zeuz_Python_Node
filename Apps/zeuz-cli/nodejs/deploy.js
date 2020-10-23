'use strict';

const axios = require('axios');
const { Command } = require('commander');
const fs = require('fs');

const DEBUG = false;

function dlog(...msg) {
    if (DEBUG) console.log(...msg);
}

async function req(options) {
    options.headers = options.headers || {};
    options.headers["Content-Type"] = "application/json";

    try {
        const response = await axios(options);
        return response.data;
    } catch (error) {
        console.error(error.message);
        if (DEBUG) console.error(error);
    }
    return null;
}

function req_token(options) {
    options.headers = {
        ...options.headers,
        "Authorization": `Bearer ${options.token}`
    };
    return req(options);
}

async function get_token_from_api(api_key, baseURL) {
    return await req({
        method: "GET",
        baseURL,
        url: "/api/auth/token/verify",
        params: { api_key }
    });
}

async function get_available_machines(token, baseURL, project, team) {
    return await req_token({
        method: "GET",
        baseURL,
        url: "/api/machines/list",
        token,
        params: { project, team, "user_level": "Automation" },
    });
}

async function get_run_status(token, baseURL, run_id) {
    return req_token({
        method: "GET",
        baseURL,
        url: "/api/run/status",
        token,
        params: { run_id },
    });
}

async function get_test_set(token, baseURL, project, team, test_set_name) {
    return req_token({
        method: "GET",
        baseURL,
        url: "/api/set/list",
        token,
        params: { project, team, "search_term": test_set_name },
    });
}

async function get_milestone(token, baseURL, project, team) {
    return req_token({
        method: "GET",
        baseURL,
        url: "/api/milestones/list",
        token,
        params: { project, team, "status": "started" },
    });
}

async function deploy(token, baseURL, data) {
    return req_token({
        method: "POST",
        baseURL,
        url: "/api/run/submit",
        data,
        token,
    });
}

function extract_runtime_parameters(param_str) {
    /*
    Extracts the JSON from the given string or file path and converts it
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
    */

    try {
        let json_str = param_str;

        // Try to see if the given argument is a file, open it.
        try {
            json_str = fs.readFileSync(param_str, "utf8");
        } catch { }

        let data = JSON.parse(json_str);
        const result = {};

        for (let key in data) {
            result[key] = { "field": key, "subfield": data[key] };
        }

        return result
    } catch (error) {
        console.error('Failed to parse JSON string/file');
    }

    return null;
}

function sleep(seconds) {
    const milliseconds = seconds * 1000;
    return new Promise((resolve) => {
        setTimeout(resolve, milliseconds);
    });
}

function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    return [year, month, day].join('-');
}

async function main() {
    const EXIT_CODE_SUCCESS = 0;
    const EXIT_CODE_ERR_NO_MACHINES = 1;
    const EXIT_CODE_ERR_INVALID_ARGS = 2;
    const EXIT_CODE_INVALID_API = 3;
    const EXIT_CODE_TEST_SET_NAME = 4;
    const EXIT_CODE_INVALID_MILESTONE = 5;
    const EXIT_CODE_INVALID_RUNTIME_PARAMETERS = 6;

    const SLEEP_TIMEOUT = 30;

    const program = new Command();

    program
        .option("--host <host:str>", "Hostname of the server")
        .option("--api_key <api_key:str>", "Your API key from Profile > API Key tab")
        .option("--test_set_name <test_set_name:str>", "Name of the test set")
        .option("--email <email:str>", "Email address where the report will be delivered")
        .option("--objective <objective:str>", "Objective of the deployment", "Deploy from CLI")
        .option("--project <project:str>", "Project ID, example: PROJ-10")
        .option("--team <team:number>", "Team ID, example: 10")
        .option("--machine <machine:number>", "Machine ID, example: 123, any (default: any)", "any")
        .option("--milestone <milestone:number>", "Milestone ID, example: 1234")
        .option("--machine_timeout <machine_timeout:number>", "Minutes to wait for any automated machine to be available (default: 60)", 60)
        .option("--report_timeout <report_timeout:number>", "Minutes to wait before reporting the deployment progress [will be reported instantly upon completion] (default: 60)", 60)
        .option("--runtime_parameters <runtime_parameters:json|file>", "Runtime parameters, must be in JSON format or a file containing JSON. (default: {})", {})
        .option("--report_filename <report_filepath:file>", "File path to save the detailed report. (default: report.json)", "report.json")

    program.parse(process.argv);

    const {
        host,
        api_key,
        test_set_name,
        email,
        objective,
        project,
        team,
        milestone,
        machine_timeout,
        report_timeout,
        report_filename,
    } = program;

    let {
        machine,
        runtime_parameters,
    } = program;

    if (runtime_parameters) {
        // Extract the runtime parameters from file or string into a python object
        runtime_parameters = extract_runtime_parameters(runtime_parameters)

        if (!runtime_parameters) {
            console.log("Invalid runtime parameters format/file.")
            return EXIT_CODE_INVALID_RUNTIME_PARAMETERS
        }
    }
    dlog("Rutnime params", runtime_parameters);

    // Parse emails
    const emails = email.split(",").map(e => e.trim());

    // Get token for the given API key
    let token = "";
    try {
        token = await get_token_from_api(api_key, host);
        token = token["token"];
        if (!token) {
            console.log("Invalid API key");
            return EXIT_CODE_INVALID_API;
        }
        dlog("Token", token);
    } catch (e) {
        console.log("Failed to fetch token");
        dlog("Token error", e);
    }

    // Verify test set
    let r = await get_test_set(token, host, project, team, test_set_name);
    if (r.length == 0) {
        console.log("Invalid test set name");
        return EXIT_CODE_TEST_SET_NAME;
    }
    dlog("Test set", r);

    // Verify milestone
    let milestone_started = false;
    r = await get_milestone(token, host, project, team);
    for (let i = 0; i < r.length; i++) {
        if (r[i]["id"] == +milestone) {
            milestone_started = true;
            break;
        }
    }
    dlog("Milestone started", milestone_started);

    if (!milestone_started) {
        console.log("Invalid milestone (either not 'started' or invalid name)");
        return EXIT_CODE_INVALID_MILESTONE;
    }

    // If 'any' is specified as the parameter for machine,
    let machine_found = false;

    for (let i = 0; i < machine_timeout; i++) {
        const machine_list = await get_available_machines(token, host, project, team);
        dlog("Machine list", machine_list);

        for (let k = 0; k < machine_list.length; k++) {
            const curr = machine_list[k];
            dlog("Machine list loop, machine id", curr["id"]);

            if (machine === "any" || machine == curr["name"]) {
                machine = curr["id"];
                machine_found = true;
                break;
            }
        }

        if (machine_found) break;
        await sleep(SLEEP_TIMEOUT);
    }
    dlog("Machine", machine);

    if (!machine_found) {
        console.log("Could not find any available automated machine... exiting");
        return EXIT_CODE_ERR_NO_MACHINES;
    }

    const payload_data = {
        "test_set_name": test_set_name,
        "dependency": { "Brower": "Chrome", "OS": "Windows" },
        "email_receiver": emails,
        "objective": objective,
        "milestone": milestone,
        "project_id": project,
        "team_id": team,
        "run_time_params": runtime_parameters,
        "machine": machine,
        "loop": "1",
        "run_time_settings": {
            "threading": false,
            "take_screenshot": true,
            "debug_mode": false,
            "upload_log_file_only_for_fail": true,
        },
        "branch_version": [],
        "start_date": formatDate(new Date()),
        "end_date": formatDate(new Date()),
        "domain": host,
    };
    dlog("payload", payload_data);

    let deploy_info = null;
    for (let i = 0; i < machine_timeout * 2; i++) {
        deploy_info = await deploy(token, host, payload_data);
        dlog("Deploy info", deploy_info);

        if (deploy_info) break;
        await sleep(SLEEP_TIMEOUT);
    }

    if (!deploy_info) {
        console.log("The specified machine is not available");
        return EXIT_CODE_ERR_NO_MACHINES;
    }

    const run_url = host + "/Home/RunID/" + deploy_info["run_id"];
    dlog("Run URL", run_url);

    // Status for complete runs
    const RUN_COMPLETE = ["complete", "cancelled"];
    let run_id_status = null;
    let report = null;

    for (let i = 0; i < 2 * report_timeout; i++) {
        const run_status = await get_run_status(token, host, deploy_info["run_id"]);
        dlog("Run status", run_status);

        run_id_status = run_status["run_id_status"].toLowerCase();

        if (RUN_COMPLETE.includes(run_id_status)) {
            report = run_status;
            break;
        }

        await sleep(SLEEP_TIMEOUT);
    }

    if (!RUN_COMPLETE.includes(run_id_status)) {
        run_id_status = "in-progress";
    }

    // Write brief report to console.
    console.log("STATUS", run_id_status);

    {
        const keys = Object.keys(report["status"]);
        const values = Object.values(report["status"]);
        for (let i = 0; i < keys.length; i++) {
            console.log(keys[i].toUpperCase(), values[i]);
        }
    }

    console.log("REPORT_URL", run_url);

    // Write detailed report to file.
    fs.writeFileSync(report_filename, JSON.stringify(report));
    console.log("REPORT_FILE", report_filename)

    return EXIT_CODE_SUCCESS;
}

(async () => {
    try {
        process.exit(await main());
    } catch (error) {
        console.error(error);
    }
})();
