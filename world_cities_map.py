#!/usr/bin/env python3
"""
Plot the 90 cities from locations.json on an interactive world map.
Saves: world_cities_map.html
"""

import json
import folium

# Load cities
with open("locations.json", "r", encoding="utf-8") as f:
    cities = json.load(f)

# Create map
m = folium.Map(
    location=[20, 0], 
    zoom_start=2,
    tiles="CartoDB positron",      # clean, modern look
    width="100%",
    height="100%"
)

# Add markers
for city in cities:
    folium.CircleMarker(
        location=[city["lat"], city["lon"]],
        radius=5,
        popup=f"<b>{city['name']}</b>",
        tooltip=city["name"],
        color="#e74c3c",
        fill=True,
        fill_color="#e74c3c",
        fill_opacity=0.85,
        weight=2
    ).add_to(m)

# Add title
title_html = '''
    <h3 align="center" style="font-size:20px">
        <b>90 Cities Global Weather Pulse</b><br>
        <small>Real-time data feed to MyDeadInternet Collective</small>
    </h3>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Save
m.save("results/world_cities_map.html")
print("✅ Interactive map saved → world_cities_map.html")
print("   Open the file in your browser to explore")