#!/usr/bin/env python3
"""
Unit Tests for world_weather_bob.py
Run with: pytest test_weather_bob.py -v
"""

import pytest
import json
import os
import math
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC
from pathlib import Path

# Import the real functions from your main script
from world_weather_bob import (
    int_guardrail,
    load_config,
    calculate_batch_sizes,
    build_compact_batch,
    make_batch_content,
    fetch_weather,
    save_full_snapshot
)

# ====================== TESTS ======================
def test_int_guardrail():
    assert int_guardrail("25") == 25
    assert int_guardrail("50", max_val=39) == 39
    assert int_guardrail("5", min_val=10) == 10
    assert int_guardrail("abc", default=21) == 21
    assert int_guardrail(None, default=30) == 30
    assert int_guardrail(15, min_val=21) == 21


def test_load_config():
    # This test requires a valid .env with API_KEY
    # We'll only test that it doesn't crash and returns expected keys
    config = load_config()
    assert "api_key" in config
    assert "max_batch" in config
    assert "target_batch" in config
    assert "calls_per_minute" in config
    assert "target_interval" in config
    assert config["api_url"] == "https://mydeadinternet.com/api/contribute"


def test_calculate_batch_sizes():
    """Test smart batching: returns list of sizes, all within MIN/MAX, sum = total"""
    for total in [125, 121, 90, 100, 50,
                   120, 23, 22, 41,
                   41, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24,
                   42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60
                   ]:
        sizes = calculate_batch_sizes(total, max_batch=39, target_batch=30)
        assert all(21-2 <= size <= 39 for size in sizes), f"Batch size out of range for total={total}: {sizes}"
        assert sum(sizes) == total, f"Sum of batches != total ({total}): {sizes}"
        assert len(sizes) >= 1


def test_build_compact_batch():
    batch = [
        {"city": "Tokyo JP", "temp_c": 15.3, "rh": 62, "wind_kmh": 12.4, "precip_mm": 0.0},
        {"city": "Nuuk GL",  "temp_c": -18.7, "rh": 71, "wind_kmh": 28.1, "precip_mm": 0.2},
    ]
    result = build_compact_batch(batch)
    expected = [
        {"n": "Tokyo JP", "c": 15.3, "h": 62, "w": 12.4, "p": 0.0},
        {"n": "Nuuk GL",  "c": -18.7, "h": 71, "w": 28.1, "p": 0.2},
    ]
    assert result == expected


def test_make_batch_content():
    batch = [
        {"city": "Tokyo JP", "temp_c": 15.3, "rh": 62, "wind_kmh": 12.4, "precip_mm": 0.0},
    ]
    content = make_batch_content(batch, batch_num=2, total_batches=4)
    assert "[WorldWx 2/4]" in content
    assert '"b":2' in content
    assert '"size":1' in content
    assert '"ts":"' in content
    assert "cities" in content


@patch("requests.get")
def test_fetch_weather_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "current": {
            "time": "2026-02-07T12:00",
            "temperature_2m": 23.4,
            "relative_humidity_2m": 65,
            "wind_speed_10m": 18.2,
            "precipitation": 0.5
        }
    }
    mock_get.return_value = mock_response

    result = fetch_weather({"name": "Tokyo JP", "lat": 35.7, "lon": 139.7})

    assert result["city"] == "Tokyo JP"
    assert result["temp_c"] == 23.4
    assert result["rh"] == 65
    assert result["wind_kmh"] == 18.2
    assert result["precip_mm"] == 0.5


@patch("requests.get")
def test_fetch_weather_failure(mock_get):
    mock_get.side_effect = Exception("Network error")
    result = fetch_weather({"name": "Test City", "lat": 0, "lon": 0})
    assert result is None


def test_save_full_snapshot(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    os.makedirs("results", exist_ok=True)

    sample_snapshot = [
        {"city": "Tokyo JP", "temp_c": 15.3, "rh": 62, "wind_kmh": 12.4, "precip_mm": 0.0}
    ]

    save_full_snapshot(sample_snapshot)

    files = list(Path("results").glob("weather-*.json"))
    assert len(files) == 1

    with open(files[0], "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "snapshot_time" in data
        assert len(data["cities"]) == 1
        assert data["cities"][0]["city"] == "Tokyo JP"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])