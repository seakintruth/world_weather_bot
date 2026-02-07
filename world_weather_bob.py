#!/usr/bin/env python3
import requests, time, os, json, random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file!")

API_URL = "https://mydeadinternet.com/api/contribute"

# ==================== RATE LIMITING CONFIG ====================
CALLS_PER_MINUTE = 6                    # 6 calls/min = 8,640 calls/day
                                        # This approaches Open-Meteo’s 10,000/day non-commercial limit
                                        # Change this value to adjust speed (e.g. 5 = 12s interval)
TARGET_INTERVAL = 60.0 / CALLS_PER_MINUTE   # → 10.0 seconds

with open("locations.json", "r") as f:
    cities = json.load(f)

def get_pulse(city):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
    try:
        d = requests.get(url, timeout=10).json()["current"]
        payload = {
            "ts": d["time"],
            "temp_c": d["temperature_2m"],
            "rh": d["relative_humidity_2m"],
            "wind_kmh": d["wind_speed_10m"],
            "precip_mm": d.get("precipitation", 0.0)
        }
        return f"""[Global Weather Pulse v1] {city['name']}
{json.dumps(payload, separators=(',', ':'))}"""
    except Exception:
        return f"[Global Weather Pulse v1] {city['name']} — API error"

if __name__ == "__main__":
    i = 0
    print(f"Starting global pulse feed @ {CALLS_PER_MINUTE} calls/min ({TARGET_INTERVAL:.1f}s interval)")

    while True:
        start_time = time.perf_counter()

        city = cities[i % len(cities)]
        pulse = get_pulse(city)

        try:
            r = requests.post(API_URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"content": pulse, "type": "pulse", "target": "the-signal"})
            print(f"[{datetime.now()}] Sent → {city['name']} | {r.status_code}")
        except Exception as e:
            print("Error:", e)

        i += 1

        elapsed = time.perf_counter() - start_time
        sleep_time = max(0.0, TARGET_INTERVAL - elapsed)
        jitter = random.uniform(-0.5, 0.5)          # prevents exact metronome
        time.sleep(sleep_time + jitter)