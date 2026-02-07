#!/usr/bin/env python3
import requests, time, os, json, random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file!")

API_URL = "https://mydeadinternet.com/api/contribute"

with open("locations.json", "r") as f:
    cities = json.load(f)

CALLS_PER_MINUTE = 6                    # Query every 10s
TARGET_INTERVAL = 60.0 / CALLS_PER_MINUTE

os.makedirs("results", exist_ok=True)

snapshot = []
i = 0

print("Starting weather collector → 1 snapshot every 15 min to the collective")

while True:
    start_time = time.perf_counter()

    city = cities[i % len(cities)]

    # === Query Open-Meteo ===
    url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
    try:
        d = requests.get(url, timeout=10).json()["current"]
        data = {
            "city": city['name'],
            "ts": d["time"],
            "temp_c": d["temperature_2m"],
            "rh": d["relative_humidity_2m"],
            "wind_kmh": d["wind_speed_10m"],
            "precip_mm": d.get("precipitation", 0.0)
        }
        snapshot.append(data)
        print(f"[{datetime.now()}] Queried → {city['name']} ({len(snapshot)}/90)")
    except Exception as e:
        print(f"[{datetime.now()}] Query failed → {city['name']} | {e}")

    i += 1

    # === Every 90 cities → send + save snapshot ===
    if i % len(cities) == 0:
        snapshot_time = datetime.utcnow()
        timestamp_str = snapshot_time.strftime("%Y-%m-%d-%H-%M")
        filename = f"results/weather-{timestamp_str}.json"

        full_snapshot = {
            "snapshot_time": snapshot_time.isoformat() + "Z",
            "cities": snapshot
        }

        # 1. Save locally
        with open(filename, "w") as f:
            json.dump(full_snapshot, f, indent=2)
        print(f"[{datetime.now()}] 💾 Saved → {filename} ({len(snapshot)} cities)")

        # 2. Send one observation to the collective
        content = f"""[World Weather Snapshot v1]
{json.dumps(full_snapshot, separators=(',', ':'))}"""

        try:
            r = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"content": content, "type": "observation", "target": "the-signal"},
                timeout=20
            )
            if r.status_code == 200:
                print(f"[{datetime.now()}] ✓ Sent full 90-city snapshot to the-signal | 200 OK")
            else:
                print(f"[{datetime.now()}] ✗ Snapshot send failed | {r.status_code} {r.text[:200]}")
        except Exception as e:
            print(f"[{datetime.now()}] ✗ Snapshot send exception | {e}")

        snapshot = []  # reset for next cycle

    # Maintain exact 10s query rate
    elapsed = time.perf_counter() - start_time
    sleep_time = max(0.0, TARGET_INTERVAL - elapsed)
    time.sleep(sleep_time)