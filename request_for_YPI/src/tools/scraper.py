# src/tools/scraper.py
import requests
import trafilatura
import os
from pathlib import Path
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

# Imports Utils
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from src.utils.logger import logger
from src.utils.pdf_extractor import is_pdf_url, extract_text_from_pdf_bytes
from src.tools.summarize_text import summarize_raw_content
# Imports RAG
from src.RAG.knowledges_graph import is_source_in_rag

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


def clean_content_with_llm(raw_text: str) -> str:
    """Nettoie le bruit (menus, pubs) sans résumer."""
    llm = get_llm(mode_or_model="fast") 
    try:
        current_dir = Path(__file__).parent.parent.parent
        text_prompt = load_text_file(os.path.join(current_dir, "prompt", "web_text_cleaning.txt"))

        prompt = ChatPromptTemplate.from_template(text_prompt)
        chain = prompt | llm
        
        truncated_text = raw_text[:300000] 
        logger.info("🧹 Nettoyage intelligent du contenu en cours...")
        try:
            result = chain.invoke({"text": truncated_text})
            logger.info("✅ Nettoyage terminé.")
        except Exception as e:
            logger.warning(f"⚠️ Échec du nettoyage LLM ({e}), utilisation du texte brut.")
            return raw_text
        return result.content
        
    except Exception as e:
        logger.warning(f"⚠️ Échec du nettoyage LLM ({e}), utilisation du texte brut.")
        return raw_text 



@tool
def read_web_page(url: str) -> str:
    """
    Scrapes URL.
    1. Returns content to Agent.
    2. Calls input_in_rag() to store clean vector data in Neo4j.
    """
    logger.info(f"Scraping : {url[:60]}...")
    
    text = None
    source_type = "WEB"
    if is_source_in_rag(url):
        text = 1
        pass

    
    try:
        response = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        
        if response.status_code != 200:
             logger.error(f"Erreur HTTP {response.status_code} pour {url}")
             return f"Error: Status Code {response.status_code}"

        content_type = response.headers.get('Content-Type', '').lower()
        
        is_pdf = (
            is_pdf_url(url) or 
            'application/pdf' in content_type or 
            response.content.startswith(b'%PDF')
        )

        if is_pdf:
            logger.debug("📄 Format PDF détecté.")
            source_type = "PDF"
            text = extract_text_from_pdf_bytes(response.content)
            if not text:
                logger.warning("PDF extraction vide.")
        else:
            text = trafilatura.extract(response.text, include_comments=False, include_tables=True)
            if not text:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.extract()
                text = soup.get_text(separator=' ', strip=True)
            text = clean_content_with_llm(text)

    except Exception as e:
        logger.error(f"❌ Exception scraping {url}: {e}")
        return f"Error processing URL: {str(e)}"

    if not text or len(text.strip()) < 50:
         return "Error: Page content seems empty or protected."


    final_text_for_agent = text
    if len(text) > 15000:
        logger.debug(f"Compression pour l'agent ({len(text)} chars)...")
        try:
            final_text_for_agent = summarize_raw_content(text)
        except Exception:
            final_text_for_agent = text[:15000] + "\n[Truncated]"

    return f"""
<DOCUMENT_CONTENT>
<URL>{url}</URL>
<TYPE>{source_type}</TYPE>
<CONTENT>
{final_text_for_agent}
</CONTENT>
</DOCUMENT_CONTENT>
"""