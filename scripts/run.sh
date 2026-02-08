#!/bin/bash
cd "$(dirname "$0")"

if pgrep -f "process.sh" > /dev/null; then
    echo "✓ Bot is already running"
    echo "   Logs → ./log/logs.txt"
    exit 0
fi

nohup ./process.sh > /dev/null 2>&1 &
echo "✓ Bot started successfully"
echo "   Logs → ./log/logs.txt"