from mitmproxy import http, ctx
import time
import csv
import os

# Initialize a list to track request details
requests_data = []


def load(l):
    # Define the custom option `output_file_path`
    ctx.options.add_option("output_file_path", str, "", "Path to output CSV file")


def request(flow: http.HTTPFlow) -> None:
    # Capture request data when it's made
    start_time = time.time()
    requests_data.append({
        'url': flow.request.url,
        'start_time': start_time,
        'status_code': None,
        'end_time': None,
        'duration': None,
        'content_length': None
    })

def response(flow: http.HTTPFlow) -> None:
    output_file_path = ctx.options.output_file_path
    create_file_if_not_exists(output_file_path)

    # print("Flow", flow)
    # print("Response", flow.response)

    res = flow.response
    end_time = time.time()

    # Find the matching request based on the URL
    for req in requests_data:
        if req['url'] == flow.request.url:
            req['status_code'] = res.status_code
            req['end_time'] = end_time
            req['duration'] = end_time - req['start_time']
            req['content_length'] = len(res.content)
            break

    # Create a list to hold the captured details
    captured_details = [
        flow.request.url,
        res.status_code,
        req.get('duration', None),
        len(res.content),
        end_time
    ]

    # Append the captured details as a row in the CSV file
    with open(output_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(captured_details)  # Write CSV row

    # Optionally print captured details for console output
    print(f"Captured: {captured_details}")

def create_file_if_not_exists(filepath):
    """
    Check if the output CSV file exists.
    If it does not exist, create the file and add csv headers.
    """

    if not os.path.exists(filepath):
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "url",
                    "status_code",
                    "duration_in_seconds",
                    "content_length_in_bytes",
                    "timestamp",
                ]
            )
        print(f"Created output file: {filepath}")
