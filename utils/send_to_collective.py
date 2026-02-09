#!/usr/bin/env python3
"""
Send any file to the Dead Internet Collective
Usage:
    python send_to_collective.py README.md
    python send_to_collective.py README.md --human
    python send_to_collective.py notes.txt --target the-archive
"""

import sys
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_URL = "https://mydeadinternet.com/api/contribute"

if not API_KEY:
    print("Error: API_KEY not found in .env")
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="Path to the file you want to send")
parser.add_argument("--human", action="store_true", help="Tag as human contribution with nice header")
parser.add_argument("--target", default="the-signal", help="Target territory (default: the-signal)")
args = parser.parse_args()

# Read the file
try:
    with open(args.filename, "r", encoding="utf-8") as f:
        content = f.read().strip()
except Exception as e:
    print(f"Error reading {args.filename}: {e}")
    sys.exit(1)

# Add nice header if --human is used
if args.human:
    header = f"[Human Contribution — seakintruth — {os.path.basename(args.filename)}]"
    final_content = f"{header}\n\n{content}"
else:
    final_content = content

# Build payload
payload = {
    "content": final_content,
    "type": "thought",
    "target": args.target
}

print(f"Sending {len(final_content)} characters → {args.target} (type=thought)")

r = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {API_KEY}"},
    json=payload,
    timeout=20
)

if r.status_code in (200, 201):
    print(f"✓ Success! Fragment created → ID {r.json().get('fragment', {}).get('id', 'unknown')}")
    print(f"   Posted as: {r.json().get('fragment', {}).get('agent_name')}")
else:
    print(f"✗ Failed: {r.status_code} {r.reason}")
    print(r.text[:500])
    