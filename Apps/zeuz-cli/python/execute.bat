python deploy.py ^
    --host "https://zeuz.zeuz.ai" ^
    --api_key "12345" ^
    --test_set_name "CLI Deployment" ^
    --email "foo@test.com, bar@test.com" ^
    --email_pref "onfail" ^
    --objective "Deploy from cli with runtime params" ^
    --project "PROJ-17" ^
    --team "2" ^
    --machine "any" ^
    --milestone "7146" ^
    --runtime_parameters "" ^
    --machine_timeout "60" ^
    --report_timeout "60" ^
    --report_filename "report.json"

@echo off
REM String: --runtime_parameters "{\"username\": \"hello\", \"password\": \"world\", \"timestamp\": \"2020-08-04\"}"
REM File: --runtime_parameters "runtime_params.json"
