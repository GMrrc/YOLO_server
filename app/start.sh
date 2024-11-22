#!/bin/bash
source venv/bin/activate

# Check if a virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "No virtual environment activated"
    exit 1
fi

# Check if nohup is installed
if ! command -v nohup &> /dev/null
then
    echo "nohup could not be found"
    exit 1
fi

# Command to execute the Python script with nohup as www-data user
nohup python3.11 ws_server.py > output_ws.log 2>&1 &
nohup python3.11 http_server.py > output_http.log 2>&1 &

# Give the server a few seconds to start
sleep 5

# Check if the process is running

if pgrep -f "python3.11 http_server.py" > /dev/null
then
    echo "Server http started successfully"
else
    echo "Server http failed to start"
    exit 1
fi

if pgrep -f "python3.11 ws_server.py" > /dev/null
then
    echo "Server ws started successfully"
else
    echo "Server ws failed to start"
    exit 1
fi

# Keep the script running
tail -f output_ws.log output_http.log
