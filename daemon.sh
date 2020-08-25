#!/bin/env bash

# Starts node_cli in the background. Make sure to login at least once
# before trying to execute this script.
# 
# If you want to kill the background process, simply find the process
# ID of zeuz node and then kill it. Example:
#   $ ps -aux | grep node_cli
#     12345   pts/1   S+    0:00   python3 node_cli.py
#   $ kill 12345

/bin/env python3 node_cli.py </dev/null &>/dev/null &
