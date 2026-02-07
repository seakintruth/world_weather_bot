#!/bin/bash
# setup_as_service.sh
# Run with: sudo ./setup_as_service.sh

set -e

echo "=== Installing Global Weather Pulse as Systemd Service ==="

# Must be run as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run with sudo"
    exit 1
fi

# Get the real user who ran sudo
REAL_USER=${SUDO_USER:-$USER}
REAL_HOME=$(eval echo ~$REAL_USER)
PROJECT_DIR="$REAL_HOME/mydeadinternet_com_bot/world_weather_bot"

echo "→ Detected user : $REAL_USER"
echo "→ Project path  : $PROJECT_DIR"

# Verify project exists
if [ ! -f "$PROJECT_DIR/run.sh" ]; then
    echo "❌ Error: run.sh not found in $PROJECT_DIR"
    exit 1
fi

# Create the systemd service
cat > /etc/systemd/system/weather-pulse.service <<EOF
[Unit]
Description=Global Weather Pulse Bot (MyDeadInternet)
After=network.target

[Service]
Type=simple
User=$REAL_USER
Group=$REAL_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/run.sh
Restart=always
RestartSec=5
StandardOutput=append:$PROJECT_DIR/log/logs.txt
StandardError=append:$PROJECT_DIR/log/logs.txt

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created"

# Reload systemd, enable and start
systemctl daemon-reload
systemctl enable weather-pulse.service
systemctl start weather-pulse.service

echo "✓ Service enabled and started"

echo ""
echo "Useful commands:"
echo "   sudo systemctl status weather-pulse"
echo "   sudo systemctl restart weather-pulse"
echo "   sudo systemctl stop weather-pulse"
echo "   journalctl -u weather-pulse -f          # live logs"
echo ""

# Show immediate status
systemctl status weather-pulse --no-pager -l