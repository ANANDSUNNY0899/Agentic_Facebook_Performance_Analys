# src/utils/metrics.py
import time
import json
import os
from typing import Dict, Any

class Metrics:
    def __init__(self):
        self.counters = {}
        self.timers = {}
        self.start_times = {}

    def incr(self, key: str, amount: int = 1):
        self.counters[key] = self.counters.get(key, 0) + amount

    def gauge(self, key: str, value):
        self.counters[key] = value

    def time_start(self, key: str):
        self.start_times[key] = time.time()

    def time_end(self, key: str):
        start = self.start_times.pop(key, None)
        if start:
            duration = time.time() - start
            self.timers[key] = duration
            return duration
        return None

    def dump(self, path: str):
        payload = {
            "counters": self.counters,
            "timers": self.timers,
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return payload
