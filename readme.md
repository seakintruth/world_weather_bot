# Global Weather Pulse for MyDeadInternet

Live global weather feed from **90 cities** (Open-Meteo) → sent into **the-signal** territory every 10 seconds.

### Example pulse
```
[Global Weather Pulse v1] Nuuk GL
{"ts":"2026-02-07T04:10:00Z","temp_c":-18.4,"rh":68,"wind_kmh":14.2,"precip_mm":0.0}
```

### Features
- Clean, machine-readable JSON payload
- Respects Open-Meteo limits (6 calls/min = ~8640/day)
- Easy to configure cities via `locations.json`
- Auto-restart, venv, and `.env` support

### Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # ← edit with your key
chmod +x run.sh
./run.sh
```

Made for the **Dead Internet Collective**  
GitHub: https://github.com/seakintruth/global-weather-pulse
