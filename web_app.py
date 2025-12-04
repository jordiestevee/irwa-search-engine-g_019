import os
from json import JSONEncoder

import httpagentparser  # for getting the user agent as json
from flask import Flask, render_template, session, request
from dotenv import load_dotenv

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document
from myapp.search.search_engine import SearchEngine
from myapp.generation.rag import RAGGenerator

load_dotenv()  # load environment variables from .env


# -------- Support for object.to_json in JSONEncoder -------- #
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)
_default.default = JSONEncoder().default
JSONEncoder.default = _default
# ----------------------------------------------------------- #


# -------- Flask application -------- #
app = Flask(__name__)
print(">>> TEMPLATE FOLDER USED BY FLASK:", app.template_folder)

app.secret_key = os.getenv("SECRET_KEY")
app.session_cookie_name = os.getenv("SESSION_COOKIE_NAME")


# -------- Instantiate engine, analytics, RAG -------- #
search_engine = SearchEngine()
analytics_data = AnalyticsData()
rag_generator = RAGGenerator()


# -------- Load products corpus -------- #
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
file_path = path + "/" + os.getenv("DATA_FILE_PATH")

corpus = load_corpus(file_path)
print("\nCorpus is loaded... \n First element:\n", list(corpus.values())[0])


# =====================================================
#                     HOME PAGE
# =====================================================
@app.route('/')
def index():
    print("Starting home url / ...")

    session['some_var'] = "Example session content"

    user_agent = request.headers.get('User-Agent')
    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)

    print("Raw user browser:", user_agent)
    print("Remote IP:", user_ip)
    print("Browser info (parsed):", agent)
    print(session)

    return render_template('index.html', page_title="Welcome")


# =====================================================
#                     SEARCH
# =====================================================
@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query'].strip()
    if not search_query:
        return render_template(
            'results.html',
            results_list=[],
            page_title="Results",
            found_counter=0,
            rag_response=None,
            search_query=search_query,
            search_id=None,
        )

    # --- NEW ANALYTICS ---
    analytics_data.record_query(search_query)
    search_id = None
    session['last_search_query'] = search_query
    session['last_search_id'] = search_id
    # ----------------------

    # run search
    results = search_engine.search(search_query, search_id, corpus)
    found_count = len(results)
    session['last_found_count'] = found_count

    # generate RAG summary
    rag_response = rag_generator.generate_response(search_query, results)
    print("RAG response:", rag_response)

    return render_template(
        'results.html',
        results_list=results,
        page_title="Results",
        found_counter=found_count,
        rag_response=rag_response,
        search_query=search_query,
        search_id=search_id,
    )



# =====================================================
#              DOCUMENT DETAILS + CLICK LOGGING
# =====================================================
@app.route('/doc_details', methods=['GET'])
def doc_details():
    clicked_doc_id = request.args.get("pid")
    search_id = request.args.get("search_id")

    if not clicked_doc_id or clicked_doc_id not in corpus:
        return render_template('doc_details.html', doc=None)

    # NEW analytics
    analytics_data.record_click(clicked_doc_id)

    # full document
    row: Document = corpus[clicked_doc_id]

    return render_template('doc_details.html', doc=row)



# =====================================================
#                         STATS PAGE
# =====================================================
@app.route('/stats')
def stats():
    metrics = analytics_data.get_metrics()
    clicks_data = analytics_data.get_document_clicks()
    query_log = analytics_data.get_query_log()

    return render_template(
        "stats.html",
        metrics=metrics,
        clicks_data=clicks_data,
        query_log=query_log,
        page_title="Stats",
    )


# =====================================================
#                         DASHBOARD
# =====================================================
@app.route('/dashboard')
def dashboard():
    # Get aggregated click data
    clicks_data = analytics_data.get_document_clicks()

    # Sort by number of clicks
    clicks_data = sorted(clicks_data, key=lambda d: d["clicks"], reverse=True)

    # Enrich with document info
    enriched_docs = []
    for entry in clicks_data:
        pid = entry["pid"]
        clicks = entry["clicks"]

        if pid in corpus:
            doc = corpus[pid]
            enriched_docs.append({
                "pid": pid,
                "clicks": clicks,
                "title": doc.title,
                "description": doc.description
            })

    return render_template(
        "dashboard.html",
        visited_docs=enriched_docs,
        page_title="Dashboard"
    )



# =====================================================
#                    TEST PLOT ENDPOINT
# =====================================================
@app.route('/plot_number_of_views', methods=['GET'])
def plot_number_of_views():
    return analytics_data.plot_number_of_views()


# =====================================================
#                       MAIN
# =====================================================
if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=os.getenv("DEBUG"))

