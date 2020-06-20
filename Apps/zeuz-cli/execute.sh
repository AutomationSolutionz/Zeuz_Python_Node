#!/bin/bash

python3 deploy.py \
    --host "https://zeuz.zeuz.ai" \
    --api_key "2392039720397290372098827309827029837" \
    --test_set_name "CLI Deployment" \
    --email "admin@zeuz.ai" \
    --objective "Deploy from cli" \
    --project "PROJ-17" \
    --team "2" \
    --machine "any" \
    --milestone "7242" \
    --machine_timeout "60" \
    --report_timeout "60"
