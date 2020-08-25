#!/bin/bash

node deploy.js \
    --host "https://zeuz.zeuz.ai" \
    --api_key "12345" \
    --test_set_name "CLI Deployment" \
    --email "hello@world.com" \
    --objective "Deploy from cli with runtime params" \
    --project "PROJ-17" \
    --team "2" \
    --machine "any" \
    --milestone "7242" \
    --runtime_parameters "" \
    --machine_timeout "60" \
    --report_timeout "60" \
    --report_filename "report.json"

# String: --runtime_parameters '{"username": "hello", "password": "world", "timestamp": "2020-08-04"}'
# File: --runtime_parameters "runtime_params.json"
