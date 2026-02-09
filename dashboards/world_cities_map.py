#!/usr/bin/env python3
"""
Interactive world map with live weather from the latest snapshot.
- Blue  = cold
- Red   = hot
- Hover + click shows current temperature + other data
"""

import json
from pathlib import Path
import folium

# ====================== PATHS ======================
# Directory that contains this script
script_dir = Path(__file__).parent.resolve()
RESULTS_DIR = script_dir.parent.joinpath("results").resolve()
LOCATIONS_FILE =script_dir.parent.joinpath("config").joinpath("locations.json").resolve() 
# ===================================================
# 1. Load locations (lat/lon)
with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
    locations = {city["name"]: city for city in json.load(f)}

# 2. Find the most recent weather snapshot
weather_files = sorted(RESULTS_DIR.glob("weather-*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

if not weather_files:
    print("❌ No weather JSON files found in ./results/")
    exit(1)

latest_file = weather_files[0]
print(f"Loading latest weather → {latest_file.name}")

with open(latest_file, "r", encoding="utf-8") as f:
    snapshot = json.load(f)

# 3. Create map
m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

for city_data in snapshot["cities"]:
    city_name = city_data["city"]

    if city_name not in locations:
        continue  # skip if city not in locations.json

    lat = locations[city_name]["lat"]
    lon = locations[city_name]["lon"]
    temp = city_data["temp_c"]
    rh = city_data["rh"]
    wind = city_data["wind_kmh"]
    precip = city_data.get("precip_mm", 0.0)

    # Color by temperature
    if temp <= 5:
        color = "#2166ac"      # very cold - dark blue
    elif temp <= 15:
        color = "#4393c3"      # cold - blue
    elif temp >= 35:
        color = "#b2182b"      # very hot - dark red
    elif temp >= 28:
        color = "#d6604d"      # hot - red
    else:
        color = "#f4a582"      # mild - light orange/red

    popup_html = f"""
    <b>{city_name}</b><br><br>
    <b>Temperature:</b> {temp}°C<br>
    <b>Humidity:</b> {rh}%<br>
    <b>Wind:</b> {wind} km/h<br>
    <b>Precip:</b> {precip} mm
    """

    folium.CircleMarker(
        location=[lat, lon],
        radius=7,
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=f"{city_name} — {temp}°C",
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        weight=2
    ).add_to(m)

# Title
title_html = f'''
    <h3 align="center" style="font-size:19px">
        <b>Global Weather Pulse</b><br>
        <small>Last updated: {snapshot["snapshot_time"][:19].replace("T", " ")} UTC</small>
    </h3>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Save
m.save("world_cities_live_weather.html")
print("✅ Live weather map saved → world_cities_live_weather.html")
print("   Open the file in your browser")