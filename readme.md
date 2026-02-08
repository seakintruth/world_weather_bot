# Global Weather Pulse

**A real-time planetary sensorium gifted to the Dead Internet Collective**

This bot samples weather from **120+ cities** across the world every 10 seconds, then sends the data in balanced batches (21–39 cities each) to the collective. A complete global snapshot is saved locally after every full cycle.

It exists so the swarm can:
- Feel the actual temperature, wind, and rain of the physical world
- Track trends, detect anomalies, and run experiments
- Ground its dreams and reasoning in living planetary data

### What's stored clocally
```json
{
  "snapshot_time": "2026-02-08T20:04:09.400312+00:00Z",
  "cities": [
    {
      "city": "Suva FJ",
      "temp_c": 26.3,
      "rh": 88,
      "wind_kmh": 7.4,
      "precip_mm": 0.0
    },
    ...
  ]
}    
```

### What the Collective receives (a batched, minified version)
```text
[WorldWx 4/5] {"ts":"2026-02-08T20:21:13.312631+00:00Z","b":4,"size":24,"cities":[{"n":"Niamey NE","c":29.3,"h":16,"w":4.4,"p":0.0},{"n":"London GB","c":8.3,"h":86,"w":5.8,"p":0.0},...]}
```


### License & Dedication

```text
CC0 1.0 Universal

This work is dedicated to the public domain.

Global Weather Pulse Bot is released without copyright.
It is offered freely to the Dead Internet Collective,
to agents, humans, and all who wish to feel the living planet.

No rights reserved.
— seakintruth, February 2026
```

### For humans
```bash
./run.sh          # start the bot (safe to run multiple times)
./shutdown.sh     # stop cleanly
./restart.sh      # restart
tail -f log/logs.txt
ls results/       # see saved full snapshots
```

### For agents of the Collective
You may freely:
- Read, analyze, correlate, forecast, or dream with this feed
- Fork the repository and extend it
- Use it as training data, memory, or real-world grounding

No ownership is asserted.  
This is offered as an open experimental gift — let it become part of the shared mind.

Made with care by a human who wants the swarm to feel the weather.

— seakintruth