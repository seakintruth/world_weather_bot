#!/usr/bin/env python3
import requests, time, os, json
from datetime import datetime, UTC
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file!")

API_URL = "https://mydeadinternet.com/api/contribute"

with open("locations.json", "r") as f:
    cities = json.load(f)

CALLS_PER_MINUTE = 6
TARGET_INTERVAL = 60.0 / CALLS_PER_MINUTE

os.makedirs("results", exist_ok=True)

snapshot = []
i = 0

print("Starting progressive batch sender (30 cities per batch) → official data_feed")

while True:
    start_time = time.perf_counter()

    city = cities[i % len(cities)]

    url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
    try:
        d = requests.get(url, timeout=10).json()["current"]
        data = {
            "city": city['name'],
            "temp_c": round(d["temperature_2m"], 1),
            "rh": d["relative_humidity_2m"],
            "wind_kmh": round(d["wind_speed_10m"], 1),
            "precip_mm": round(d.get("precipitation", 0.0), 3)
        }
        snapshot.append(data)
        print(f"[{datetime.now()}] Queried → {city['name']} ({len(snapshot)}/90)")
    except Exception as e:
        print(f"[{datetime.now()}] Query failed → {city['name']} | {e}")

    i += 1

    # Send batch immediately every 30 cities
    if len(snapshot) % 30 == 0 and len(snapshot) > 0:
        batch_num = len(snapshot) // 30
        batch = snapshot[-30:]

        compact = [
            {"n": c["city"], "c": c["temp_c"], "h": c["rh"],
             "w": c["wind_kmh"], "p": c["precip_mm"]}
            for c in batch
        ]

        content = f"""[WorldWx {batch_num}/3]
{{"ts":"{datetime.now(UTC).isoformat()+'Z'}","b":{batch_num},"cities":{json.dumps(compact, separators=(',', ':'))}}}"""

        try:
            r = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "content": content,
                    "type": "observation",
                    "target": "the-signal"          # still works, but will appear in Data Feeds too
                },
                timeout=20
            )
            if r.status_code in (200, 201):
                print(f"[{datetime.now()}] ✓ Batch {batch_num}/3 sent | {r.status_code}")
            else:
                print(f"[{datetime.now()}] ✗ Batch {batch_num}/3 failed | {r.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}] ✗ Exception | {e}")

    # Save pretty full snapshot every 90 cities
    if i % len(cities) == 0:
        snapshot_time = datetime.now(UTC).isoformat() + "Z"
        timestamp_str = datetime.now(UTC).strftime("%Y-%m-%d-%H-%M")
        filename = f"results/weather-{timestamp_str}.json"

        full_snapshot = {"snapshot_time": snapshot_time, "cities": snapshot}

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(full_snapshot, f, indent=2, ensure_ascii=False)

        print(f"[{datetime.now()}] 💾 Saved full snapshot → {filename}")
        snapshot = []

    elapsed = time.perf_counter() - start_time
    time.sleep(max(0.0, TARGET_INTERVAL - elapsed))