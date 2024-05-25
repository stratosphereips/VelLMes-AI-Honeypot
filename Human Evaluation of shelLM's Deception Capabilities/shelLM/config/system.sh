#!/bin/bash

cd /opt/system 2>/dev/null

# Using a variable for the timestamp to avoid repetition and potential mismatch
timestamp=$(date "+%Y.%m.%d-%H.%M.%S")
log_path="/opt/system/logs/${timestamp}_script.log"

script -q -f -a "$log_path" --command "python tool.py -e .env -c configSSH.yml -m 'ft:gpt-3.5-turbo-1106:stratosphere-laboratory::8KS2seKA'" 2>/dev/null | tee -a /opt/system/logs/system.log 2>/dev/null

logout