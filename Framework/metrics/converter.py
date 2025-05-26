import json
import os
from pathlib import Path
from google.cloud import bigquery
from datetime import datetime


credential_path = Path.cwd() / 'node-bigquery-privkey.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credential_path)
client = bigquery.Client()
previous_ts_format = "%d/%m/%Y %H:%M:%S.%f"
bq_format = "%Y-%m-%d %H:%M:%S.%f"


def read_from_bigquery():
    query = """
    select
        execution_log,
        metrics
    from
        `node-bigquery-367604.zeuz_node.reports_telus_nov28`
    where
        STARTS_WITH(run_id, 'Mon-Nov-28');
    """

    queryJob = client.query(query)
    data = queryJob.result()
    result = []
    for d in data:
        result.append((
            json.loads(d.execution_log),
            json.loads(d.metrics),
        ))
    return result


def convert_ts(prev_ts):
    return datetime.strftime(
        datetime.strptime(prev_ts, previous_ts_format),
        # prev_ts,
        bq_format,
    )


def send_to_bigquery(execution_log, metrics):
    client = bigquery.Client()
    action_table_id = "node-bigquery-367604.zeuz_node.zeuz_metrics_node_actions"
    steps_table_id = "node-bigquery-367604.zeuz_node.zeuz_metrics_node_steps"

    run_id = execution_log["run_id"]
    tc_id = execution_log["test_cases"][0]["testcase_no"]

    steps = metrics["node"]["steps"]
    actions = metrics["node"]["actions"]
    try:
        browser_perf = metrics["browser_performance"]["default"]
    except:
        browser_perf = list()

    # A dict of step id to step name
    step_names = {}
    for step in steps:
        if "id" not in step:
            return
        step_names[step["id"]] = step["name"]


    def send_actions_metrics():
        for action in actions:
            action["run_id"] = run_id
            action["tc_id"] = tc_id
            if "step_id" not in action:
                continue
            action["step_name"] = step_names[action["step_id"]]
            action["time_stamp"] = convert_ts(action["timestamp"])
            del action["timestamp"]

        rows_to_insert = actions
        errors = client.insert_rows_json(action_table_id, rows_to_insert)
        if len(errors) == 0:
            print("Sent action metrics report to BigQuery")
        else:
            print(f"Encountered errors while inserting rows: {errors}")


    def send_steps_metrics():
        for step in steps:
            step["run_id"] = run_id
            step["tc_id"] = tc_id
            step["step_id"] = step["id"]
            del step["id"]
            step["step_name"] = step["name"]
            del step["name"]
            step["step_sequence"] = step["sequence"]
            del step["sequence"]
            step["time_stamp"] = convert_ts(datetime.today())
            if "actions" in step:
                del step["actions"]

        rows_to_insert = steps
        errors = client.insert_rows_json(steps_table_id, rows_to_insert)
        if len(errors) == 0:
            print("Sent step metrics report to BigQuery")
        else:
            print(f"Encountered errors while inserting rows: {errors}")


    def send_browser_perf_metrics():
        rows_to_insert = json.dumps(browser_perf)


    send_actions_metrics()
    # send_steps_metrics()
    send_browser_perf_metrics()


def main():

    data = read_from_bigquery()
    for execution_log, metrics in data:
        send_to_bigquery(execution_log, metrics)

    # with open("sample_metrics.json", "r") as f:
    #     data = json.load(f)

    # A dict of step id to step name
    # step_names = {}
    # for step in steps:
    #     step_names[step["id"]] = step["name"]
    # data = convert(data)

main()
