"""
Minimal agent using SerpAPI for web search and Mistral LLM for synthesis.
Requires:
  - MISTRAL_API_KEY in environment
  - SERPAPI_API_KEY in environment
  - pip install mistralai serpapi python-dotenv
"""
import os
import sys


# =============================================================================
# SerpAPI Search Setup (with fallback)
# =============================================================================
try:
    # try LangChain wrapper (old API)
    from langchain.utilities import SerpAPIWrapper
    search = SerpAPIWrapper()  # if available, same interface: search.run(query)
    print("Using LangChain SerpAPIWrapper")
except Exception:
    # fallback to serpapi package (direct client) if LangChain wrapper not present
    try:
        from serpapi import GoogleSearch
    except Exception:
        raise RuntimeError(
            "No SerpAPI client available. Install 'serpapi' (pip install serpapi) "
            "or install a langchain version that provides SerpAPIWrapper."
        )

    SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")
    if not SERPAPI_API_KEY:
        raise RuntimeError("SERPAPI_API_KEY not set in environment")

    def _serpapi_run(query: str) -> str:
        """Execute a Google search via SerpAPI and return formatted results."""
        params = {"engine": "google", "q": query, "api_key": SERPAPI_API_KEY}
        search_client = GoogleSearch(params)
        res = search_client.get_dict()
        # Try to extract useful fields; adapt to your needs
        organic = res.get("organic_results") or []
        # build a compact textual summary
        snippets = []
        for item in organic[:8]:
            title = item.get("title", "")
            snippet = item.get("snippet") or item.get("rich_snippet", {}).get("top", {}).get("extensions", "")
            link = item.get("link", "")
            snippets.append(f"{title}\n{snippet}\n{link}")
        return "\n\n".join(snippets) if snippets else str(res)

    class _SearchWrapper:
        """Wrapper to provide a .run(query) interface compatible with LangChain tools."""
        def run(self, q: str) -> str:
            return _serpapi_run(q)

    search = _SearchWrapper()
    print("Using direct SerpAPI client (serpapi package)")

# =============================================================================
# Mistral LLM Setup
# =============================================================================
from mistralai import Mistral

mistral_api_key = os.environ.get("MISTRAL_API_KEY")
if not mistral_api_key:
    print("Warning: MISTRAL_API_KEY not set in env", file=sys.stderr)

mistral_client = Mistral(api_key=mistral_api_key)


def call_mistral(prompt: str, model: str = "mistral-small-latest") -> str:
    """
    Call Mistral LLM via the chat completions API.
    Available models: mistral-tiny, mistral-small-latest, mistral-medium-latest, mistral-large-latest
    """
    try:
        response = mistral_client.chat.complete(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # Extract the assistant's reply
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling Mistral: {e}"


# =============================================================================
# Simple Agent Flow: Search + Synthesis
# =============================================================================
def run_agent(query: str) -> str:
    """
    Minimal agent that:
    1. Searches the web using SerpAPI
    2. Passes results to Mistral for synthesis
    """
    print(f"\n[Agent] Searching for: {query}")
    search_result = search.run(query)
    print(f"[Agent] Search results retrieved ({len(search_result)} chars)")

    # Build prompt for Mistral
    prompt = f"""You are a helpful assistant. Use the following web search results to answer the user's question.
Cite sources (URLs) when possible. Be concise and factual.

=== Web Search Results ===
{search_result}

=== User Question ===
{query}

=== Your Answer ===
"""
    print("[Agent] Calling Mistral LLM...")
    answer = call_mistral(prompt)
    return answer


# =============================================================================
# Main Entry Point
# =============================================================================
if __name__ == "__main__":
    # Check environment variables
    if not os.environ.get("SERPAPI_API_KEY"):
        print("Error: SERPAPI_API_KEY not set. Export it or add to .env", file=sys.stderr)
        sys.exit(1)
    if not os.environ.get("MISTRAL_API_KEY"):
        print("Error: MISTRAL_API_KEY not set. Export it or add to .env", file=sys.stderr)
        sys.exit(1)

    # Example query
    test_query = "What is the current population of Senegal?"
    print("=" * 60)
    print("Running agent with query:", test_query)
    print("=" * 60)

    result = run_agent(test_query)

    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    print(result)