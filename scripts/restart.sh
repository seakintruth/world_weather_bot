#!/bin/bash
# restart.sh - Properly stop then start the bot

cd "$(dirname "$0")"

echo "=== Restarting Global Weather Pulse Bot ==="

echo "→ Stopping bot..."
./shutdown.sh

sleep 2

echo "→ Starting bot again..."
./run.sh

echo "✓ Restart completed successfully"