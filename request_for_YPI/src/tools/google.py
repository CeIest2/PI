# src/tools/google.py
import os
import json
from src.utils.logger import logger
import requests
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv
import re

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

# Imports de vos modules
from src.RAG.input_in_rag import input_in_rag
from src.utils.pdf_extractor import is_pdf_url
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from src.utils.index_information import get_definition
from src.utils.eval_utility import evaluate_document_relevance
from src.tools.scraper import read_web_page

@tool
def search_google(query: str, include_pdfs: bool = True) -> list[dict]:
    """
    Primary search engine for finding EXTERNAL context, news, laws, or technical reports.
    """
    load_dotenv()
    print(f"🔎 [Google] Searching: {query}")
    api_key = os.getenv("GOOGLE_API_KEY")
    cx_id = os.getenv("GOOGLE_CX_ID")
    
    if not api_key or not cx_id:
        print("❌ Erreur : GOOGLE_API_KEY ou GOOGLE_CX_ID manquant dans .env")
        return [{"error": "Missing Google API keys"}]
    
    endpoint = "https://www.googleapis.com/customsearch/v1"
    
    search_query = query if include_pdfs else f"{query} -filetype:pdf"
    
    params = {
        'key': api_key, 'cx': cx_id, 'q': search_query,
        'num': 5, 'gl': 'us', 'lr': 'lang_en'
    }
    
    resp = requests.get(endpoint, params=params)
    data = resp.json()
    
    if 'error' in data:
        error_msg = data['error'].get('message', 'Erreur inconnue')
        print(f"🔴 GOOGLE API ERROR: {error_msg}")
        return [{"error": error_msg}]
    
    results = []
    for item in data.get('items', []):
        link = item.get("link", "")
        
        if is_pdf_url(link) and not include_pdfs:
            continue
            
        results.append({
            "title": item.get("title"),
            "link": link,
            "snippet": item.get("snippet"),
            "content_type": "pdf" if is_pdf_url(link) else "web"
        })
            
    return results

def process_single_link(res, country, indicator_name, resilience_index):
    if not isinstance(res, dict) or "link" not in res:
        return None

    title   = res.get('title', 'No Title')
    link    = res.get('link', '')
    snippet = res.get('snippet', 'No snippet')

    page_content = read_web_page.run(link)

    if not page_content or "Error:" in page_content[:50]:
        return None

    reponse_eval = evaluate_document_relevance(
        summarized_text=page_content, 
        country=country, 
        indicator_name=indicator_name, 
        indicator_definition=resilience_index
    )
    if reponse_eval.get("decision") == "KEEP":
        print(f"      ✅ [KEPT] {title[:40]}")
        # if is it keep we can put in our rag
        try:

            match = re.search(r"<CONTENT>(.*?)</CONTENT>", page_content, re.DOTALL)
            if match:
                raw_text_content = match.group(1).strip()
            else:
                raw_text_content = page_content

            source_type = "PDF" if  link.lower().endswith(".pdf") else "WEB"

            input_in_rag(raw_text_content, link, source_type)
            
        except Exception as e:
            logger.error(f"      ⚠️ Erreur insertion RAG: {e}")


        return f"SOURCE: {title}\nLINK: {link}\nSNIPPET: {snippet}\n\nCONTENU DÉTAILLÉ:\n{page_content[:300000]}..."
    else:
        print(f"      ❌ [DISCARDED] {title[:40]} - Reason: {reponse_eval.get('reason', 'No reason provided')}")
    return None

def run_deterministic_investigation(internal_data: str, country: str, indicator_name: str, mode: str = "smart"):
    """
    Orchestrateur principal : Génération requêtes -> Recherche Parallèle -> Analyse Parallèle.
    """
    llm = get_llm("smart")
    resilience_index = get_definition(indicator_name)
    
    print(f"\n🔧 [Phase 1] Planification & Recherche pour {country}...")

    prompt = ChatPromptTemplate.from_template(load_text_file(os.path.join("prompt", "search_planning.txt")))
    response = (prompt | llm).invoke({
        "internal_data": internal_data[:3000], 
        "country": country,
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "resilience_index": resilience_index,
        "indicator_name": indicator_name
    })

    # Parsing JSON (Simplifié)
    try:
        content = response.content.replace("```json", "").replace("```", "").strip()
        queries = json.loads(content)
    except Exception as e:
        print(f"⚠️ Erreur JSON ({e}), utilisation des requêtes par défaut.")
        queries = [f"{indicator_name} obstacles {country}", f"{indicator_name} strategy {country}"]
    queries = queries
    print(f"   📋 {len(queries)} requêtes générées. Lancement parallèle...")

    raw_results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_query = {executor.submit(search_google.run, q): q for q in queries}
        
        for future in concurrent.futures.as_completed(future_to_query):
            try:
                res = future.result()
                if isinstance(res, list):
                    raw_results.extend(res)
            except Exception as e:
                print(f"   ❌ Erreur sur une requête Google : {e}")


    unique_results = {r['link']: r for r in raw_results if isinstance(r, dict) and 'link' in r}.values()

    final_findings = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        future_to_link = {
            executor.submit(process_single_link, item, country, indicator_name, resilience_index): item 
            for item in unique_results
        }
        
        for future in concurrent.futures.as_completed(future_to_link):
            try:
                result = future.result()
                if result:
                    final_findings.append(result)
            except Exception as exc:
                logger.error(f"      💥 Erreur sur un lien : {exc}")

    logger.info(f"   ✅ Fin. {len(final_findings)} documents retenus.")
    return "\n\n".join(final_findings)