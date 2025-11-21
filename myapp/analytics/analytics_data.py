import json
import random
import altair as alt
import pandas as pd
import time
import uuid
from collections import defaultdict, Counter


class AnalyticsData:
    """
    In-memory persistence.
    Backward compatible with boilerplate + extended for Part 4 report.
    """

    # old table (web_app directly uses this)
    fact_clicks = dict([])

    # new tables (optional use in report)
    dim_sessions = dict([])
    fact_requests = []
    fact_queries = dict([])
    fact_click_events = dict([])

    def save_query_terms(self, terms: str) -> int:
        # still returns a random query id as seminar expected
        qid = random.randint(0, 100000)

        # also store query terms in a richer table for your report
        self.fact_queries[str(qid)] = {
            "ts": time.time(),
            "raw_query": terms,
            "terms": terms.lower().split(),
            "num_terms": len(terms.split())
        }
        return qid

    def plot_number_of_views(self):
        data = [{'Document ID': doc_id, 'Number of Views': count}
                for doc_id, count in self.fact_clicks.items()]
        df = pd.DataFrame(data) if data else pd.DataFrame(columns=["Document ID", "Number of Views"])

        chart = alt.Chart(df).mark_bar().encode(
            x='Document ID',
            y='Number of Views'
        ).properties(
            title='Number of Views per Document'
        )
        return chart.to_html()

    # ---- optional richer helpers for report/dashboard ----
    def metrics(self):
        total_queries = len(self.fact_queries)
        total_clicks = sum(self.fact_clicks.values()) if self.fact_clicks else 0
        ctr = total_clicks / max(1, total_queries)

        top_queries = Counter([q["raw_query"] for q in self.fact_queries.values()]).most_common(10)

        return {
            "total_queries": total_queries,
            "total_clicks": total_clicks,
            "ctr": ctr,
            "top_queries": top_queries
        }

    def plot_top_queries(self):
        data = [{"Query": q, "Count": c} for q, c in self.metrics()["top_queries"]]
        df = pd.DataFrame(data) if data else pd.DataFrame(columns=["Query", "Count"])

        chart = alt.Chart(df).mark_bar().encode(
            x="Count:Q",
            y=alt.Y("Query:N", sort="-x")
        ).properties(title="Top Queries")
        return chart.to_html()


class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter

    def to_json(self):
        return self.__dict__

    def __str__(self):
        # safer than json.dumps(self)
        return json.dumps(self.__dict__)
