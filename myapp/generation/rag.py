# myapp/generation/rag.py

import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

"""We improved the baseline RAG by (1) tightening the prompt to enforce grounding and PID citations, 
(2) enriching the retrieved context with product metadata, 
and (3) adding a confidence gate that returns a “no good products” fallback when retrieval is weak."""

class RAGGenerator:

    IMPROVED_PROMPT_TEMPLATE = """
You are an expert product advisor helping users choose the best option from retrieved e-commerce products.

Rules:
- Use ONLY the retrieved products below. Do not invent products or attributes.
- If products are irrelevant or insufficient, return ONLY:
"There are no good products that fit the request based on the retrieved results."
- Cite products using their PID like [PID].

Task:
1. Pick the single best product for the user's request.
2. Explain why, using concrete attributes (price, discount, rating, category, brand).
3. Optionally mention one alternative if clearly second-best.

Retrieved Products:
{retrieved_results}

User Request:
{user_query}

Output Format:
- Best Product: [PID] Title
- Why: ...
- Alternative (optional): [PID] Title — short reason
"""

    def generate_response(self, user_query: str, retrieved_results: list, top_N: int = 20) -> str:
        """
        Returns a STRING (web_app.py expects this).
        """
        DEFAULT_ANSWER = "RAG is not available. Check your credentials (.env file) or account limits."

        # ---- No-good-products gate ----
        if not retrieved_results:
            return "There are no good products that fit the request based on the retrieved results."

        top_score = getattr(retrieved_results[0], "ranking", 0.0) or 0.0
        if float(top_score) < 0.5:   # tune if your BM25 scores are smaller/larger
            return "There are no good products that fit the request based on the retrieved results."

        try:
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            model_name = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

            def fmt(res):
                return (
                    f"- PID: {res.pid} | Title: {res.title} "
                    f"| Price: {getattr(res, 'selling_price', 'n/a')} "
                    f"| Discount: {getattr(res, 'discount', 'n/a')} "
                    f"| Rating: {getattr(res, 'average_rating', 'n/a')} "
                    f"| Brand: {getattr(res, 'brand', 'n/a')} "
                    f"| Category: {getattr(res, 'category', 'n/a')}"
                )

            formatted_results = "\n".join([fmt(r) for r in retrieved_results[:top_N]])

            prompt = self.IMPROVED_PROMPT_TEMPLATE.format(
                retrieved_results=formatted_results,
                user_query=user_query
            )

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
                temperature=0.2
            )

            return chat_completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error during RAG generation: {e}")
            return DEFAULT_ANSWER
