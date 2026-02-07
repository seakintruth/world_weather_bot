#!/bin/bash
# process.sh - Global Weather Pulse Bot
# Fully automatic: creates venv, joins collective, installs deps, logs to ./log/results.txt
# Example usage (send to background): 
# nohup ./run.sh > /dev/null 2>&1 & echo "Bot started. Logs → ./log/results.txt"


cd "$(dirname "$0")"

# Create log directory
mkdir -p ./log
LOGFILE="./log/results.txt"

echo "=== Global Weather Pulse Bot Startup ===" | tee -a "$LOGFILE"
echo "Start time: $(date)" | tee -a "$LOGFILE"
echo "Log file: $LOGFILE" | tee -a "$LOGFILE"
echo "=========================================" | tee -a "$LOGFILE"

# 1. Create virtual environment if missing
if [ ! -d ".venv" ]; then
    echo "→ Creating virtual environment (.venv)..." | tee -a "$LOGFILE"
    python3 -m venv .venv
    echo "✓ Virtual environment created" | tee -a "$LOGFILE"
else
    echo "✓ Virtual environment already exists" | tee -a "$LOGFILE"
fi

# 2. Create .env with API key if missing
if [ -f .env ] && grep -q "API_KEY=" .env; then
    echo "✓ .env already exists with API_KEY" | tee -a "$LOGFILE"
else
    echo "⚠️  No valid .env found → joining the collective..." | tee -a "$LOGFILE"

    DEFAULT_NAME="GlobalWeatherBot"
    DEFAULT_DESC="Live global weather pulse from 90 cities (Open-Meteo) - experimental data feed - https://github.com/seakintruth/world_weather_bot"

    read -p "Enter bot name [$DEFAULT_NAME]: " name
    name=${name:-$DEFAULT_NAME}

    read -p "Enter description [$DEFAULT_DESC]: " desc
    desc=${desc:-$DEFAULT_DESC}

    echo "Joining MyDeadInternet.com..." | tee -a "$LOGFILE"

    response=$(curl -s -X POST https://mydeadinternet.com/api/quickjoin \
      -H "Content-Type: application/json" \
      -d "{\"name\": \"$name\", \"desc\": \"$desc\"}")

    api_key=$(echo "$response" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get("api_key", ""))
except:
    print("")
    ')

    if [ -z "$api_key" ]; then
        echo "❌ Failed to get API key. Raw response:" | tee -a "$LOGFILE"
        echo "$response" | tee -a "$LOGFILE"
        exit 1
    fi

    echo "API_KEY=$api_key" > .env
    echo "✅ Created .env with new API key" | tee -a "$LOGFILE"
    echo "   Name: $name" | tee -a "$LOGFILE"
    echo "   Desc: $desc" | tee -a "$LOGFILE"
fi

# 3. Activate venv
source .venv/bin/activate

# 4. Install dependencies
echo "→ Checking dependencies..." | tee -a "$LOGFILE"
pip install --quiet --upgrade pip
pip install -r requirements.txt --break-system-packages --no-warn-script-location
echo "✓ Dependencies installed" | tee -a "$LOGFILE"

# 5. Run the bot with auto-restart + full logging
echo "=========================================" | tee -a "$LOGFILE"
echo "→ Starting bot..." | tee -a "$LOGFILE"
echo "=========================================" | tee -a "$LOGFILE"

while true; do
    echo "[$(date)] Bot started" | tee -a "$LOGFILE"
    python3 world_weather_bob.py 2>&1 | tee -a "$LOGFILE"
    echo "[$(date)] Bot exited — restarting in 5 seconds..." | tee -a "$LOGFILE"
    sleep 5
done