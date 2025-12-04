import os
import json
from datetime import datetime

ANALYTICS_FILE = os.path.join("data", "analytics.json")


class AnalyticsData:

    def __init__(self):
        self._ensure_file()

    # -----------------------------------
    def _ensure_file(self):
        if not os.path.exists(ANALYTICS_FILE):
            data = {"queries": [], "clicks": []}
            self._save(data)

    def _load(self):
        with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data):
        with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # -----------------------------------
    # Record a query
    def record_query(self, query):
        data = self._load()
        data["queries"].append({
            "query": query,
            "timestamp": datetime.now().isoformat()
        })
        self._save(data)

    # Record a click
    def record_click(self, pid):
        data = self._load()
        data["clicks"].append({
            "pid": pid,
            "timestamp": datetime.now().isoformat()
        })
        self._save(data)

    # -----------------------------------
    # Metrics for Stats
    def get_metrics(self):
        data = self._load()
        total_queries = len(data["queries"])
        total_clicks = len(data["clicks"])
        avg_clicks = (total_clicks / total_queries) if total_queries else 0

        return {
            "total_queries": total_queries,
            "total_clicks": total_clicks,
            "avg_clicks_per_query": round(avg_clicks, 2)
        }

    # Data for dashboard chart
    def get_document_clicks(self):
        data = self._load()
        freq = {}
        for c in data["clicks"]:
            pid = c["pid"]
            freq[pid] = freq.get(pid, 0) + 1
        return [{"pid": pid, "clicks": count} for pid, count in freq.items()]

    # Query log for stats page
    def get_query_log(self):
        data = self._load()
        return data["queries"]
    


# -----------------------------------
# Optional minimal object to keep compatibility
class ClickedDoc:
    def __init__(self, pid, description, counter):
        self.pid = pid
        self.description = description
        self.counter = counter

