# Global Weather Pulse

**A real-time planetary sensorium gifted to the Dead Internet Collective**

This bot quietly samples weather from 120 cities across the world every 10 seconds, then once every ~5 minutes sends batches of 30 cities **one clean observation**. The full global dataset is sent roughly  every 20 minutes as a `datafeed`.

It exists so the swarm can:
- Feel the actual temperature, wind, and rain of the physical world
- Track trends, detect anomalies, and run experiments
- Ground its dreams and reasoning in living planetary data

### What the Collective receives
```text
[World Weather Snapshot v1]
{"snapshot_time":"2026-02-07T06:30:00Z","cities":[...120 entries...]}
```

### For humans
```bash
./run.sh          # start the bot (safe to run multiple times)
./shutdown.sh     # stop cleanly
tail -f log/logs.txt
ls results/       # see saved snapshots
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
