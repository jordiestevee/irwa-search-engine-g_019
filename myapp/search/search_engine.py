import random
import numpy as np
import re
import math
from collections import defaultdict, Counter

from myapp.search.objects import Document

class SearchEngine:
    """Implements BM25 search over the corpus (cached index)."""

    def __init__(self):
        self._indexed = False
        self._index = defaultdict(list)   # term -> [(pid, tf), ...]
        self._idf = {}
        self._doc_len = {}
        self._avgdl = 0.0
        self._N = 0

    def _tokenize(self, text: str):
        text = (text or "").lower()
        return re.findall(r"[a-z0-9]+", text)

    def _build_index(self, corpus: dict):
        self._index.clear()
        self._idf.clear()
        self._doc_len.clear()

        df_counts = Counter()
        self._N = len(corpus)
        lens = []

        for pid, doc in corpus.items():
            # Safe access to fields that may/may not exist
            title = getattr(doc, "title", "") or ""
            desc = getattr(doc, "description", "") or ""
            brand = getattr(doc, "brand", "") or ""
            category = getattr(doc, "category", "") or ""
            subcat = getattr(doc, "sub_category", "") or ""

            tokens = self._tokenize(f"{title} {desc} {brand} {category} {subcat}")
            counts = Counter(tokens)

            dl = sum(counts.values())
            self._doc_len[str(pid)] = dl
            lens.append(dl)

            for term, tf in counts.items():
                self._index[term].append((str(pid), tf))
                df_counts[term] += 1

        self._avgdl = (sum(lens) / len(lens)) if lens else 0.0

        # BM25 style IDF
        for term, dfi in df_counts.items():
            self._idf[term] = math.log((self._N - dfi + 0.5) / (dfi + 0.5) + 1)

        self._indexed = True

    def _bm25_scores(self, terms, candidates, k1=1.5, b=0.75):
        scores = defaultdict(float)
        for t in terms:
            if t not in self._index:
                continue
            idf_t = self._idf.get(t, 0.0)
            for pid, tf in self._index[t]:
                if pid not in candidates:
                    continue
                dl = self._doc_len.get(pid, 1)
                denom = tf + k1 * (1 - b + b * (dl / (self._avgdl or 1)))
                scores[pid] += idf_t * (tf * (k1 + 1)) / denom
        return scores

    def search(self, search_query, search_id, corpus, num_results=20):
        print("Search query:", search_query)

        if not self._indexed:
            self._build_index(corpus)

        terms = self._tokenize(search_query)
        if not terms:
            return []

        # Soft matching: union of candidate docs for any query term
        candidates = set()
        for t in terms:
            if t in self._index:
                candidates |= {pid for pid, _ in self._index[t]}

        if not candidates:
            return []

        scores = self._bm25_scores(terms, candidates)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:num_results]

        results = []
        for pid, score in ranked:
            doc = corpus[pid]

            # Keep URL format compatible with web_app.py
            url = "doc_details?pid={}&search_id={}&param2=2".format(pid, search_id)

            results.append(Document(
                pid=doc.pid,
                title=doc.title,
                description=doc.description,
                url=url,
                ranking=float(score)
            ))

        return results