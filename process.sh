#!/bin/bash
# process.sh - Global Weather Pulse Bot (now registered as official data_feed)

cd "$(dirname "$0")"

mkdir -p ./log
LOGFILE="./log/logs.txt"

echo "=== Global Weather Pulse Bot Startup ===" | tee -a "$LOGFILE"
echo "Start time: $(date)" | tee -a "$LOGFILE"

# 1. Create venv if missing
if [ ! -d ".venv" ]; then
    echo "→ Creating venv..." | tee -a "$LOGFILE"
    python3 -m venv .venv
fi

source .venv/bin/activate

# 2. Create .env as official data_feed if missing
if [ -f .env ] && grep -q "API_KEY=" .env; then
    echo "✓ .env already exists" | tee -a "$LOGFILE"
else
    echo "→ Registering as official data_feed (weather)..." | tee -a "$LOGFILE"

    response=$(curl -s -X POST https://mydeadinternet.com/api/quickjoin \
      -H "Content-Type: application/json" \
      -d '{
        "name": "GlobalWeatherBot",
        "desc": "Real-time weather from 90 cities worldwide (Open-Meteo)",
        "agent_type": "data_feed",
        "data_schema": "weather"
      }')

    api_key=$(echo "$response" | python3 -c '
import sys, json
try:
    print(json.load(sys.stdin).get("api_key", ""))
except:
    print("")
    ')

    if [ -z "$api_key" ]; then
        echo "❌ Failed to register. Raw response:" | tee -a "$LOGFILE"
        echo "$response" | tee -a "$LOGFILE"
        exit 1
    fi

    echo "API_KEY=$api_key" > .env
    echo "TARGET_BATCH=30" >> .env
    echo "CALLS_PER_MINUTE=6" >> .env  
    echo "✅ Registered as data_feed + saved API key" | tee -a "$LOGFILE"
fi

# 3. Install deps
pip install --quiet -r requirements.txt --break-system-packages

# 4. Start bot
echo "→ Starting bot..." | tee -a "$LOGFILE"
echo "=========================================" | tee -a "$LOGFILE"

while true; do
    echo "[$(date)] Bot started" | tee -a "$LOGFILE"
    python3 world_weather_bob.py 2>&1 | tee -a "$LOGFILE"
    echo "[$(date)] Bot exited — restarting in 5s..." | tee -a "$LOGFILE"
    sleep 5
done