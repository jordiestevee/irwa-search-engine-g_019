import re
import math
from collections import defaultdict, Counter

from myapp.search.objects import Document, ResultItem


class SearchEngine:
    """BM25 search over the product corpus (cached in memory)."""

    def __init__(self):
        self._indexed = False
        self._index = defaultdict(list)   # term -> [(pid, tf), ...]
        self._idf = {}
        self._doc_len = {}
        self._avgdl = 0.0
        self._N = 0

    # ---------- Text processing ----------

    def _tokenize(self, text: str):
        text = (text or "").lower()
        return re.findall(r"[a-z0-9]+", text)

    # ---------- Index building ----------

    def _build_index(self, corpus: dict):
        """
        Build an in-memory BM25 index from the corpus of Document objects.
        """
        self._index.clear()
        self._idf.clear()
        self._doc_len.clear()

        df_counts = Counter()
        self._N = len(corpus)
        lengths = []

        for pid, doc in corpus.items():
            title = getattr(doc, "title", "") or ""
            desc = getattr(doc, "description", "") or ""
            brand = getattr(doc, "brand", "") or ""
            category = getattr(doc, "category", "") or ""
            subcat = getattr(doc, "sub_category", "") or ""

            tokens = self._tokenize(f"{title} {desc} {brand} {category} {subcat}")
            counts = Counter(tokens)

            dl = sum(counts.values())
            self._doc_len[str(pid)] = dl
            lengths.append(dl)

            for term, tf in counts.items():
                self._index[term].append((str(pid), tf))
                df_counts[term] += 1

        self._avgdl = (sum(lengths) / len(lengths)) if lengths else 0.0

        # BM25-style IDF
        for term, dfi in df_counts.items():
            self._idf[term] = math.log((self._N - dfi + 0.5) / (dfi + 0.5) + 1)

        self._indexed = True

    # ---------- BM25 scoring ----------

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

    # ---------- Public search API ----------

    def search(self, search_query: str, search_id: int, corpus: dict, num_results: int = 20):
        """
        Main entry point used from web_app.py.

        :param search_query: user query string
        :param search_id: id returned by AnalyticsData.save_query_terms
        :param corpus: dict[pid -> Document]
        :param num_results: how many top results to return
        :return: list[ResultItem]
        """
        print("Search query:", search_query)

        if not self._indexed:
            self._build_index(corpus)

        terms = self._tokenize(search_query)
        if not terms:
            return []

        # Soft matching: docs that contain any of the query terms
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
            doc: Document = corpus[pid]

            # internal link (goes to our Flask detail page)
            internal_url = f"doc_details?pid={pid}&search_id={search_id}"

            result = ResultItem(
                pid=doc.pid,
                title=doc.title,
                description=doc.description,
                url=internal_url,
                ranking=float(score),
                selling_price=doc.selling_price,
                discount=doc.discount,
                average_rating=doc.average_rating,
                brand=doc.brand,
                category=doc.category,
                source_url=doc.url,
                images=doc.images,
            )
            results.append(result)

        return results
