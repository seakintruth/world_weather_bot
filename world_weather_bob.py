#!/usr/bin/env python3
import requests
import time
import os
import json
import math
from datetime import datetime, UTC
from dotenv import load_dotenv

def int_guardrail(value, default=21, min_val=1, max_val=39):
    """Safely convert to int and clamp value."""
    try:
        val = int(value)
    except (TypeError, ValueError):
        val = default
    return max(min_val, min(max_val, val))

def load_config():
    """Load and validate all configuration from .env."""
    load_dotenv()

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in .env file!")

    target_batch = int_guardrail(os.getenv("TARGET_BATCH"), default=30, min_val=1, max_val=40)
    max_batch = (target_batch+5)

    calls_per_minute = int_guardrail(os.getenv("CALLS_PER_MINUTE"), default=6, min_val=1, max_val=30)
    target_interval = 60.0 / calls_per_minute

    return {
        "api_key": api_key,
        "api_url": "https://mydeadinternet.com/api/contribute",
        "max_batch": max_batch,
        "target_batch": target_batch,
        "calls_per_minute": calls_per_minute,
        "target_interval": target_interval
    }


def load_cities():
    with open("config/locations.json", "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_batch_sizes(total: int, target_batch: int = 30, max_batch: int = 39) -> list[int]:
    """Evenly distributed batching using ceiling division."""
    if total == 0:
        return []
    if total <= max_batch:
        return [total]

    num_batches = max(1, math.ceil(total / target_batch))

    base = total // num_batches
    remainder = total % num_batches

    sizes = [base + 1] * remainder + [base] * (num_batches - remainder)

    # Only clamp the maximum size
    sizes = [min(max_batch, size) for size in sizes]

    return sizes

def fetch_weather(city: dict) -> dict | None:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
    try:
        d = requests.get(url, timeout=10).json()["current"]
        return {
            "city": city["name"],
            "temp_c": round(d["temperature_2m"], 1),
            "rh": d["relative_humidity_2m"],
            "wind_kmh": round(d["wind_speed_10m"], 1),
            "precip_mm": round(d.get("precipitation", 0.0), 1)
        }
    except Exception as e:
        print(f"Query failed → {city['name']} | {e}")
        return None

def build_compact_batch(batch: list) -> list:
    return [
        {"n": c["city"], "c": c["temp_c"], "h": c["rh"],
         "w": c["wind_kmh"], "p": c["precip_mm"]}
        for c in batch
    ]

def make_batch_content(batch: list, batch_num: int, total_batches: int) -> str:
    compact = build_compact_batch(batch)
    return f"""[WorldWx {batch_num}/{total_batches}]
{{"ts":"{datetime.now(UTC).isoformat()+'Z'}","b":{batch_num},"size":{len(batch)},"cities":{json.dumps(compact, separators=(',', ':'))}}}"""

def post_observation(content: str, api_key: str, api_url: str):
    try:
        r = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"content": content, "type": "observation", "target": "the-signal"},
            timeout=20
        )
        if r.status_code in (200, 201):
            print(f"[{datetime.now()}] ✓ Batch sent | {r.status_code}")
        else:
            print(f"[{datetime.now()}] ✗ Batch failed | {r.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] ✗ Post exception | {e}")

def save_full_snapshot(snapshot: list):
    snapshot_time = datetime.now(UTC).isoformat() + "Z"
    timestamp_str = datetime.now(UTC).strftime("%Y-%m-%d-%H-%M")
    filename = f"results/weather-{timestamp_str}.json"

    full_snapshot = {"snapshot_time": snapshot_time, "cities": snapshot}

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(full_snapshot, f, indent=2, ensure_ascii=False)

    print(f"[{datetime.now()}] 💾 Saved full snapshot → {filename} ({len(snapshot)} cities)")

# ====================== MAIN ======================
def main():
    config = load_config()

    cities = load_cities()
    batch_sizes = calculate_batch_sizes(
        len(cities),
        config["target_batch"],
        config["max_batch"]
    )
    print(f"Loaded {len(cities)} cities → batch sizes = {batch_sizes}")

    snapshot = []
    full_data = []
    batch_index = 0
    city_index = 0

    while True:
        start_time = time.perf_counter()

        city = cities[city_index]

        data = fetch_weather(city)
        if data:
            snapshot.append(data)
            full_data.append(data)
            print(f"[{datetime.now()}] Queried → {city['name']} ({len(snapshot)}/{batch_sizes[batch_index]})")

        city_index += 1

        if len(snapshot) == batch_sizes[batch_index]:
            content = make_batch_content(snapshot, batch_index + 1, len(batch_sizes))
            post_observation(content, config["api_key"], config["api_url"])
            snapshot = []
            batch_index += 1

            if batch_index >= len(batch_sizes):
                batch_index = 0

        if city_index % len(cities) == 0 and city_index > 0:
            save_full_snapshot(full_data)
            full_data = []
            snapshot = []

        elapsed = time.perf_counter() - start_time
        time.sleep(max(0.0, config["target_interval"] - elapsed))

if __name__ == "__main__":
    main()