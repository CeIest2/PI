# src/tools/google.py
import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv

@tool
def search_google(query: str) -> list[dict]:
    """
    Use this tool to search Google for recent information, facts, or news.
    Returns a list of titles and URLs (PDFs are excluded).
    """
    print(f"🔎 [Google] Searching: {query}")
    
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    cx_id = os.getenv("GOOGLE_CX_ID")
    
    if not api_key or not cx_id:
        print("❌ Erreur : GOOGLE_API_KEY ou GOOGLE_CX_ID manquant dans .env")
        return [{"error": "Missing Google API keys"}]

    endpoint = "https://www.googleapis.com/customsearch/v1"
    
    # ASTUCE : On peut aussi ajouter "-filetype:pdf" à la requête pour que Google filtre lui-même
    # params['q'] = query + " -filetype:pdf"
    
    params = {
        'key': api_key,
        'cx': cx_id,
        'q': query,
        'num': 5, # On demande 5 résultats
        'gl': 'us',
        'lr': 'lang_en'
    }

    try:
        resp = requests.get(endpoint, params=params)
        data = resp.json()
        
        if 'error' in data:
            error_msg = data['error'].get('message', 'Erreur inconnue')
            print(f"🔴 GOOGLE API ERROR: {error_msg}")
            return [{"error": f"Google API Error: {error_msg}"}]

        results = []
        if 'items' in data:
            for item in data['items']:
                link = item.get("link", "")
                
                # --- MODIFICATION ICI : FILTRAGE DES PDF ---
                # Si le lien termine par .pdf (en minuscule), on l'ignore
                if link.lower().endswith(".pdf"):
                    print(f"📄 PDF ignoré : {link}")
                    continue 
                # -------------------------------------------

                results.append({
                    "title": item.get("title"),
                    "link": link,
                    "snippet": item.get("snippet")
                })
        else:
            print("⚠️ Google a répondu 200 OK mais sans 'items'")
            
        return results

    except Exception as e:
        print(f"❌ Exception Python : {str(e)}")
        return [{"error": str(e)}]