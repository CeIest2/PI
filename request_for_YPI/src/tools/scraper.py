# src/tools/scraper.py
import requests
import trafilatura
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from src.utils.logger import logger  # Utilisation de votre nouveau logger
from src.utils.pdf_extractor import is_pdf_url, extract_text_from_pdf_bytes
from pathlib import Path
import os

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

def summarize_raw_content(text: str) -> str:
    """Condenses raw text."""
    # ... (votre code existant inchangé) ...
    # Juste pour l'exemple, je mets un pass, gardez votre logique
    llm = get_llm(mode_or_model="fast")
    try:
        # Chemin relatif à adapter selon votre structure
        prompt_path = os.path.join("prompt", "summarize_raw_content.txt")
        text_prompt = load_text_file(prompt_path)
    except:
        text_prompt = "Summarize this: {text}"

    prompt = ChatPromptTemplate.from_template(text_prompt)
    chain = prompt | llm
    result = chain.invoke({"text": text[:80000]})
    return result.content

@tool
def read_web_page(url: str) -> str:
    """
    Scrapes URL via Requests (Download ONCE strategy).
    Detects PDF content automatically via headers or bytes.
    """
    logger.info(f"Scraping : {url[:60]}...")
    
    text = None
    source_type = "WEB"
    
    try:
        # 1. TÉLÉCHARGEMENT UNIQUE (Centralisé)
        # On désactive la vérification SSL si besoin (verify=False) mais attention en prod
        response = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        
        if response.status_code != 200:
             logger.error(f"Erreur HTTP {response.status_code} pour {url}")
             return f"Error: Status Code {response.status_code}"

        content_type = response.headers.get('Content-Type', '').lower()
        
        # 2. DÉTECTION DU TYPE (PDF ou WEB)
        # On regarde l'URL, le Header, ou les "Magic Bytes" du fichier (%PDF)
        is_pdf = (
            is_pdf_url(url) or 
            'application/pdf' in content_type or 
            response.content.startswith(b'%PDF')
        )

        # 3. EXTRACTION
        if is_pdf:
            logger.debug("Format PDF détecté. Extraction depuis la mémoire...")
            source_type = "PDF"
            # On utilise la fonction qui prend les BYTES directement
            text = extract_text_from_pdf_bytes(response.content)
            
            if not text:
                logger.warning("PDF détecté mais extraction vide (image ou protégé ?)")

        else:
            # Mode Web classique
            # Trafilatura est excellent pour le texte propre
            text = trafilatura.extract(response.text, include_comments=False, include_tables=True)
            
            # Fallback BeautifulSoup si Trafilatura échoue
            if not text:
                logger.debug("Trafilatura vide, tentative BeautifulSoup...")
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.extract()
                text = soup.get_text(separator=' ', strip=True)

    except Exception as e:
        logger.error(f"Exception critique scraping {url}: {e}")
        return f"Error processing URL: {str(e)}"

    # 4. VALIDATION & COMPRESSION
    if not text or len(text.strip()) < 50:
         return "Error: Page content seems empty or protected."
    
    logger.debug(f"Contenu extrait : {len(text)} caractères")

    final_text = text
    if len(text) > 15000: # Seuil de compression
        logger.debug(f"Compression en cours ({len(text)} chars)...")
        try:
            final_text = summarize_raw_content(text)
            logger.debug(f"Compressé vers {len(final_text)} chars.")
        except Exception as e:
            logger.error(f"Erreur compression: {e}")
            final_text = text[:15000] + "\n[Truncated]"
        
    return f"""
<DOCUMENT_CONTENT>
<URL>{url}</URL>
<TYPE>{source_type}</TYPE>
<CONTENT>
{final_text}
</CONTENT>
</DOCUMENT_CONTENT>
"""