#!/bin/bash
# run.sh - Smart startup script for Global Weather Pulse Bot

cd "$(dirname "$0")"

echo "=== Global Weather Pulse Bot Startup ==="

# === 1. Create .env with API key if missing ===
if [ -f .env ] && grep -q "API_KEY=" .env; then
    echo "✓ .env already exists with API_KEY"
else
    echo "⚠️  No .env found or missing API_KEY → joining the collective..."

    # Default values
    DEFAULT_NAME="GlobalWeatherBot"
    DEFAULT_DESC="Live global weather pulse from 90 cities (Open-Meteo) - experimental data feed"

    read -p "Enter bot name [$DEFAULT_NAME]: " name
    name=${name:-$DEFAULT_NAME}

    read -p "Enter description [$DEFAULT_DESC]: " desc
    desc=${desc:-$DEFAULT_DESC}

    echo "Joining MyDeadInternet.com..."

    response=$(curl -s -X POST https://mydeadinternet.com/api/quickjoin \
      -H "Content-Type: application/json" \
      -d "{\"name\": \"$name\", \"desc\": \"$desc\"}")

    # Parse api_key using Python (reliable fallback)
    api_key=$(echo "$response" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get("api_key", ""))
except:
    print("")
    ')

    if [ -z "$api_key" ]; then
        echo "❌ Failed to get API key. Raw response:"
        echo "$response"
        exit 1
    fi

    echo "API_KEY=$api_key" > .env
    echo "✅ Successfully created .env with new API key"
    echo "   Name: $name"
    echo "   Desc: $desc"
fi

# === 2. Activate venv ===
source .venv/bin/activate

# === 3. Install dependencies if needed ===
echo "Checking dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# === 4. Run the bot with auto-restart ===
echo "========================================="
echo "Starting bot..."
echo "========================================="

while true; do
    echo "[$(date)] Bot started"
    python world_weather_bob.py
    echo "[$(date)] Bot exited — restarting in 5 seconds..."
    sleep 5
done