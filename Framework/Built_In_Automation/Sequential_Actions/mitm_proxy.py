from mitmproxy import http
import time
import sys
import csv
import os

# Initialize a list to track request details
requests_data = []

# Get the output file path from command-line arguments
output_file_path = sys.argv[3] if len(sys.argv) > 3 else 'default_output.csv'
print(f"OUTPUT: {output_file_path}")

# Create a CSV file and write headers if the file does not exist
if not os.path.exists(output_file_path):
    with open(output_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["url", "status_code", "duration in seconds", "content_length in bytes", "timestamp"])  # Write CSV header

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
