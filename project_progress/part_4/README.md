# Information Retrieval & Web Analytics - Search Engine Project

This project implements a complete Information Retrieval (IR) system for an e-commerce dataset. It features a Flask-based web interface, a custom BM25 search algorithm, a Retrieval-Augmented Generation (RAG) system for AI summaries, and a custom Web Analytics dashboard to track user behavior.


## Features
* **Search Engine:** Fast BM25 ranking algorithm with "lazy indexing" and soft-matching optimization.
* **RAG Integration:** Generates AI summaries of search results using the Groq API (Llama 3), featuring a "No Good Products" relevance gate.
* **Web Interface:** Clean UI for searching, viewing results, and inspecting product details.
* **Analytics Dashboard:** Tracks queries, clicks, and calculates CTR (Click-Through Rate).
* **Data Validation:** Uses Pydantic to ensure clean handling of prices, ratings, and missing data.

## Prerequisites
* **Python 3.8+**
* **Groq API Key** (for RAG functionality)

## Installation & Setup


1.  **Create and activate a virtual environment:**
   ```bash
  python -m venv venv
  venv\Scripts\activate
   ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the root directory.
2.  Add your Groq API key to enable the RAG features:
    ```env
    GROQ_API_KEY=your_actual_api_key_here
    GROQ_MODEL=llama-3.1-8b-instant
    ```

## How to Run

1.  **Start the Flask Application:**
    ```bash
    flask run web_app.py
    ```

2.  **Access the Web Interface:**
    Open your web browser and navigate to:
    `http://127.0.0.1:5000`

## Project Architecture & Algorithms

### 1. Search Algorithm (BM25)
Located in `myapp/search/search_engine.py`.

* **Indexing:** The system builds an inverted index in memory upon the first search request (Lazy Loading).
* **Ranking:** Uses the **BM25** probabilistic scoring function.
* **Optimization:** Implements a "Soft Match" pre-filter. 
* **Tokenization:** Simple regex-based tokenization removes punctuation and converts text to lowercase.


### 2. Retrieval-Augmented Generation (RAG)
Located in `myapp/generation/rag.py`.

* **Logic Gate:** Before calling the AI, the system checks the relevance score of the top result. If the score is `< 0.5`, it bypasses the LLM and returns: *"There are no good products that fit the request..."*
* **Metadata Injection:** The prompt context is enriched not just with titles, but with **Price**, **Discount**, and **Rating**, allowing the LLM to make data-driven recommendations.

### 3. File Structure
* `web_app.py`: Entry point for the Flask server.
* `myapp/search/`: Contains `search_engine.py`, `algorithms.py`, and `objects.py` (Pydantic models).
* `myapp/generation/`: Contains `rag.py` (Groq API integration).
* `myapp/analytics/`: Contains `analytics_data.py` (JSON-based logger).
* `data/`: Stores the corpus and the `analytics.json` log file.

## Web Analytics

The application tracks user interactions locally in `data/analytics.json`.

* **Dashboard:** Accessible via the "Dashboard" link in the navbar (`/dashboard`).
* **Metrics Tracked:**
    * **Most Visited Documents** 
    * **Click Distribution Chart**
    * **Average clicks per query**  
    * **Recent Queries**

---
**Group Members:**
- **u215114** Albert Jané  
- **u215108** Jordi Esteve  
- **u198732** Marc de los Aires  
