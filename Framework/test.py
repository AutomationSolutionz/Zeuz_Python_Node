import os
import subprocess
from Utilities import CommonUtil
from pathlib import Path

OUTPUT_FILEPATH = "/Users/sakib/Documents/zeuz/Zeuz_Python_Node/AutomationLog/debug_sakib_dd446e56-a_AaRlG/session_1/TEST-10894/zeuz_download_folder/proxy_log/mitm.log"
CAPTURED_CSV_FILEPATH = "/Users/sakib/Documents/zeuz/Zeuz_Python_Node/AutomationLog/debug_sakib_dd446e56-a_AaRlG/session_1/TEST-10894/zeuz_download_folder/proxy_log/captured_network_data.csv"
MITM_PROXY_PATH = "/Users/sakib/Documents/zeuz/Zeuz_Python_Node/Framework/Built_In_Automation/Sequential_Actions/mitm_proxy.py"
PORT = 8080 


print(f"Starting proxy server on port {PORT}")

print(f"MITM Proxy path: {MITM_PROXY_PATH}")
print(f"Proxy Log file: {OUTPUT_FILEPATH}")

print(f"Captured Network file: {CAPTURED_CSV_FILEPATH}")

# Open the output file in append mode
with open(OUTPUT_FILEPATH, 'a') as output_file:
    # Start the subprocess
    process = subprocess.Popen(
        ['mitmdump', '-s', MITM_PROXY_PATH, '-w', str(CAPTURED_CSV_FILEPATH), '-p', str(PORT)],
        stdout=output_file,  # Redirect stdout to the file
        stderr=output_file   # Redirect stderr to the file
    )
    
pid = process.pid

# Assuming CommonUtil.mitm_proxy_pids is a list, make sure it's initialized properly
if not hasattr(CommonUtil, 'mitm_proxy_pids'):
    CommonUtil.mitm_proxy_pids = []

CommonUtil.mitm_proxy_pids.append(pid)

import time
time.sleep(2)

# Verify if the service is running on the specified port
def verify_port_in_use(port):
    if os.name == 'posix':  # macOS/Linux
        result = subprocess.run(['lsof', '-i', f':{port}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    elif os.name == 'nt':  # Windows
        result = subprocess.run(['netstat', '-aon'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout if f':{port}' in result.stdout else ''

# Check if the port is in use
port_status = verify_port_in_use(PORT)

if port_status:
    print(f"Service is running on port {PORT}:\n{port_status}")
else:
    print(f"Service is NOT running on port {PORT}. Check if the subprocess started correctly.")

# Prevent the script from exiting immediately
input("Press Enter to exit...\n")