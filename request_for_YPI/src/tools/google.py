# src/tools/google.py
import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
from src.utils.pdf_extractor import is_pdf_url


@tool
def search_google(query: str, include_pdfs: bool = True) -> list[dict]:
    """
    Primary search engine for finding EXTERNAL context, news, laws, or technical reports.
    
    Args:
        query: The search query string (keywords).
        include_pdfs: If True, includes PDFs (good for official reports).
    """
    load_dotenv()
    print(f"🔎 [Google] Searching: {query}")
    api_key = os.getenv("GOOGLE_API_KEY")
    cx_id = os.getenv("GOOGLE_CX_ID")
    
    if not api_key or not cx_id:
        print("❌ Erreur : GOOGLE_API_KEY ou GOOGLE_CX_ID manquant dans .env")
        return [{"error": "Missing Google API keys"}]
    
    endpoint = "https://www.googleapis.com/customsearch/v1"
    
    # Si on veut exclure les PDFs au niveau de Google Search
    search_query = query
    if not include_pdfs:
        search_query = query + " -filetype:pdf"
    
    params = {
        'key': api_key,
        'cx': cx_id,
        'q': search_query,
        'num': 5, 
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
                
                # Détection du type de contenu
                if is_pdf_url(link):
                    if include_pdfs:
                        print(f"📄 PDF détecté : {link}")
                        results.append({
                            "title": item.get("title"),
                            "link": link,
                            "snippet": item.get("snippet"),
                            "content_type": "pdf"
                        })
                    else:
                        print(f"📄 PDF ignoré : {link}")
                        continue
                else:
                    # Contenu web classique
                    results.append({
                        "title": item.get("title"),
                        "link": link,
                        "snippet": item.get("snippet"),
                        "content_type": "web"
                    })
        else:
            print("⚠️ Google a répondu 200 OK mais sans 'items'")
            
        print(f"✅ [Google] {len(results)} résultats retournés")
        return results
        
    except Exception as e:
        print(f"❌ Exception Python : {str(e)}")
        return [{"error": str(e)}]