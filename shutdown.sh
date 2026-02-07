#!/bin/bash
# shutdown.sh - Fully stop the weather bot (compatible with all pkill versions)

cd "$(dirname "$0")"
LOGFILE="./log/logs.txt"

echo "=== Shutting down Global Weather Pulse Bot ===" | tee -a "$LOGFILE"
echo "Time: $(date)" | tee -a "$LOGFILE"

killed=false

# Kill the actual Python bot
if pgrep -f "world_weather_bob.py" > /dev/null; then
    echo "→ Killing world_weather_bob.py ..." | tee -a "$LOGFILE"
    pkill -f "world_weather_bob.py"
    sleep 0.8
    pkill -9 -f "world_weather_bob.py" 2>/dev/null
    killed=true
fi

# Kill the launcher script
if pgrep -f "process.sh" > /dev/null; then
    echo "→ Killing process.sh ..." | tee -a "$LOGFILE"
    pkill -f "process.sh"
    sleep 0.8
    pkill -9 -f "process.sh" 2>/dev/null
    killed=true
fi

if [ "$killed" = true ]; then
    echo "✓ Bot has been fully stopped" | tee -a "$LOGFILE"
else
    echo "✓ Bot was not running" | tee -a "$LOGFILE"
fi

echo "=========================================" | tee -a "$LOGFILE"