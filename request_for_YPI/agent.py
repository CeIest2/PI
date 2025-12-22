import os
import requests
from bs4 import BeautifulSoup
from mistralai import Mistral
import wikipedia
import time

# Import du nouveau module PDF depuis utils
from utils.pdf_extractor import is_pdf_url, extract_text_from_pdf_url

# ==============================================================================
# 🔑 ZONE DE CONFIGURATION
# ==============================================================================


# ==============================================================================
# 1. CERVEAU LLM (MISTRAL)
# ==============================================================================
def call_mistral(prompt: str, mode: str = "fast", step_name: str = "") -> str:
    model = "mistral-small-latest" if mode == "fast" else "mistral-large-latest"
    print(f"       [Mistral] Thinking with '{model}' ({step_name})...")
    MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY") 
    client = Mistral(api_key=MISTRAL_API_KEY)
    try:
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content
        if isinstance(raw, list):
            final_text = ""
            for chunk in raw:
                if hasattr(chunk, 'type') and chunk.type == 'text':
                    final_text += chunk.text
            return final_text
        return str(raw)
    except Exception as e:
        print(f"      ❌ [Error] Mistral API: {e}")
        return "ERROR"

# ==============================================================================
# 2. MOTEUR DE RECHERCHE (GOOGLE API OFFICIELLE)
# ==============================================================================
def search_google_api(query: str, num: int = 3):
    print(f"   [Google API] Searching for: '{query}'...")
    GOOGLE_API_KEY  = os.environ.get("GOOGLE_API_KEY") 
    GOOGLE_CX_ID    = os.environ.get("GOOGLE_CX_ID") 
    
    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CX_ID,
        'q': query,
        'num': num,
        'gl': 'us',    
        'lr': 'lang_en'
    }

    try:
        resp = requests.get(endpoint, params=params)
        data = resp.json()
        
        if 'error' in data:
            print(f"   [Google Error] {data['error']['message']}")
            return []

        links = []
        if 'items' in data:
            print(f"\n  ---  RAW RESULTS FOUND ({len(data['items'])}) ---")
            
            for i, item in enumerate(data['items']):
                title = item.get("title", "No Title")
                link = item.get("link", "No Link")
                snippet = item.get("snippet", "No Snippet")
                
                print(f"  [{i+1}] {title}")
                print(f"      link: {link}")
                
                # Détection du type de contenu
                content_type = "web"
                if is_pdf_url(link):
                    content_type = "pdf"
                    print(f"      type: 📄 PDF détecté")
                
                links.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "source": content_type
                })
            print("  -----------------------------------------\n")
        
        return links

    except Exception as e:
        print(f"   [Error] Google Request failed: {e}")
        return []

# ==============================================================================
# 3. LECTURE & ANALYSE (SCRAPING + PDF)
# ==============================================================================
def scrape_and_clean(item: dict, max_chars: int = 25000) -> str:
    """
    Extrait le contenu d'une source (web HTML, PDF ou Wikipedia).
    Gère automatiquement le type de contenu.
    """
    # Cas Wikipedia
    if item.get("source") == "wiki":
        try:
            return wikipedia.page(item['title'], auto_suggest=False).content[:max_chars]
        except: 
            pass

    url = item['link']
    
    # Cas PDF
    if item.get("source") == "pdf" or is_pdf_url(url):
        print(f"     [Reading PDF] Extracting: {url}...")
        pdf_text = extract_text_from_pdf_url(url, max_chars=max_chars)
        
        if pdf_text and len(pdf_text) > 100:
            return pdf_text
        else:
            print(f"     [Warning] PDF extraction failed. Fallback to snippet.")
            return f"PDF content unavailable. Google Summary: {item.get('snippet', '')}"
    
    # Cas HTML classique
    print(f"     [Reading HTML] Visiting: {url}...")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer", "form", "svg", "iframe"]):
            tag.extract()
            
        text = ' '.join(soup.get_text(separator=' ').split())
        print(f"     [Reading] Success ({len(text)} chars extracted).")
        return text[:max_chars]
        
    except Exception as e:
        print(f"     [Warning] Site blocked or failed. Fallback to Google snippet.")
        return f"Page content unavailable. Google Summary: {item.get('snippet', '')}"

def analyze_content(content: str, query: str, url: str) -> str:
    if not content or len(content) < 50: 
        return None
    
    prompt = f"""
    Analyze this text to answer: "{query}"
    Text (Source: {url}):
    {content[:25000]}
    
    If completely irrelevant, reply "REJECT".
    Otherwise, extract key facts/figures concisely.
    """
    
    analysis = call_mistral(prompt, mode="fast", step_name="Filtering")
    
    if "REJECT" in analysis or len(analysis) < 10:
        print(f"        [Filter] Content rejected by LLM.")
        return None
    
    print(f"      ✅ [Filter] Content kept.")
    return f"SOURCE: {url}\nNOTES:\n{analysis}\n"

# ==============================================================================
# 4. ORCHESTRATEUR
# ==============================================================================
def search_wikipedia_fallback(query: str):
    print(f"\n   [Fallback] Switching to Wikipedia...")
    links = []
    try:
        wikipedia.set_lang("en")
        titles = wikipedia.search(query, results=2)
        print(f"   [Wikipedia] Titles found: {titles}")
        for title in titles:
            try:
                page = wikipedia.page(title, auto_suggest=False)
                links.append({"title": page.title, "link": page.url, "source": "wiki"})
            except: 
                continue
    except: 
        pass
    return links

def run_agent(context_text: str) -> str:
    query = context_text
    print("\n" + "="*60)
    print(f" AGENT ACTIVATION: '{query}'")
    print("="*60 + "\n")
    investigation_queries = generate_investigation_queries(context_text)

    internet_knowledge = ""
    print(f"{investigation_queries=}")
    
    for q in investigation_queries:
        links = search_google_api(q, num=3)
        
        knowledge = ""
        valid_count = 0
        
        if links:
            print(f"\n---  WEB EXPLORATION ---\n")
            for item in links:
                raw_text = scrape_and_clean(item)
                info = analyze_content(raw_text, q, item['link'])
                if info:
                    knowledge += info + "\n---\n"
                    valid_count += 1

        if valid_count == 0:
            wiki_links = search_wikipedia_fallback(q)
            if wiki_links:
                print(f"\n---  WIKI EXPLORATION ---\n")
                for item in wiki_links:
                    raw_text = scrape_and_clean(item)
                    info = analyze_content(raw_text, query, item['link'])
                    if info:
                        knowledge += info + "\n---\n"
                        valid_count += 1

        if valid_count == 0:
            return "❌ Sorry, I found no relevant information."

        print("\n" + "="*60)
        print(f"  FINAL SYNTHESIS ({valid_count} sources used)")
        print("="*60)
        
        final_prompt = f"""
        User Question: "{query}"
        Based ONLY on the following verified notes, write a comprehensive, professional answer.
        Cite your sources (URLs) explicitly.
        NOTES:
        {knowledge}
        """
        internet_knowledge += call_mistral(final_prompt, mode="fast", step_name="Synthesis") + "\n\n"

    synthesized_prompt = """
    You are an expert strategic intelligence analyst.
    Based on the following collected internet knowledge, provide a concise, well-structured summary answer to the user's question."""
    internet_knowledge = call_mistral(synthesized_prompt + internet_knowledge, mode="smart", step_name="Final Answer")
    return internet_knowledge.strip()


def generate_investigation_queries(contexte_texte: str) -> list:
    prompt = f"""
    You are a strategic intelligence planner for Internet infrastructure policy.

    TASK:
    Generate exactly 3 distinct, high-precision Google Search queries (in English) to investigate the "WHY" behind these numbers.
    
    The queries must target:
    1. **Regulatory/Legal**: National broadband plans, telecom laws, censorship decrees, budget allocations.
    2. **Infrastructure**: Specific fiber backbone projects, IXP outage reports, submarine cable faults.
    3. **Stakeholders**: Reports on the dominant ISP, the Telecom Regulator's annual report, or World Bank digital projects.

    OUTPUT FORMAT:
    Return ONLY a Python list of strings. Do not write anything else.
    Example: ["internet research 1", "internet research 2", "internet research 3"]
    Here is the context to consider:
    {contexte_texte}
    """
 
    try:
        response = call_mistral(prompt, mode="smart", step_name="Génération Requêtes")
        
        if "[" in response and "]" in response:
            start = response.find('[')
            end = response.rfind(']') + 1
            list_str = response[start:end]
            return eval(list_str)
        else:
            raise ValueError("Format de liste non trouvé")

    except Exception as e:
        print(f"⚠️ Erreur génération requêtes : {e}")
        return []


if __name__ == "__main__":
    question = "How many XRP have we in the US ?"

    respond = run_agent(question)

    print("#########################################")
    print(respond)