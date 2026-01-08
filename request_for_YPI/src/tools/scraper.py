import requests
import trafilatura
import fitz  # PyMuPDF
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from pathlib import Path
import os
from src.utils.pdf_extractor import is_pdf_url, extract_text_from_pdf_url

# Headers RENFORCÉS pour passer les sécurités (CISA, Gouv, etc.)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

def summarize_raw_content(text: str) -> str:
    """Condenses raw text."""
    llm = get_llm(mode_or_model="fast")
    current_dir = Path(__file__).parent.parent.parent
    
    # Gestion d'erreur si le fichier prompt n'existe pas
    try:
        text_prompt = load_text_file(os.path.join(current_dir, "prompt", "summarize_raw_content.txt"))
    except:
        text_prompt = "Summarize this: {text}"

    prompt = ChatPromptTemplate.from_template(text_prompt)
    chain = prompt | llm
    
    # On limite pour éviter les crashs sur gros fichiers
    result = chain.invoke({"text": text[:80000]})
    return result.content

@tool
def read_web_page(url: str) -> str:
    """
    Scrapes URL via Requests using robust headers.
    Handles PDF directly from memory to avoid 403 double-fetch.
    """
    print(f"👀 [Scraper] Reading: {url}")
    
    text = None
    source_type = "WEB"

    if is_pdf_url(url):
        try:
            print("   ↳ 📄 Extension .pdf détectée. Tentative extraction directe...")
            text = extract_text_from_pdf_url(url)
            if text:
                source_type = "PDF"
        except Exception:
            print("   ⚠️ Échec extraction directe (probablement 403). Passage en mode manuel...")
            text = None

    if not text:
        try:
            response = requests.get(url, headers=HEADERS, timeout=20, verify=False)
            
            if response.status_code != 200:
                 return f"Error: Could not fetch URL {url} (Status Code: {response.status_code})."

            content_type = response.headers.get('Content-Type', '').lower()
            
            # --- CAS A : C'est un PDF (détecté via Header ou Signature) ---
            if 'application/pdf' in content_type or response.content.startswith(b'%PDF'):
                print("   ↳ 📄 PDF détecté (Bytes). Extraction depuis la mémoire RAM...")
                source_type = "PDF"
                
                try:
                    with fitz.open(stream=response.content, filetype="pdf") as doc:
                        text_list = []
                        for page in doc:
                            text_list.append(page.get_text())
                        text = "\n".join(text_list)
                except Exception as e:
                    return f"Error parsing PDF bytes: {e}"

            # --- CAS B : Page Web Standard ---
            else:
                text = trafilatura.extract(response.text, include_comments=False, include_tables=True)
                
                # Fallback BeautifulSoup
                if not text:
                    print("   ↳ ⚠️ Trafilatura failed, trying BeautifulSoup...")
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, "html.parser")
                    for script in soup(["script", "style"]):
                        script.extract()
                    text = soup.get_text(separator=' ', strip=True)

        except Exception as e:
            return f"Error processing URL: {str(e)}"

    # Validation finale
    if not text or len(text.strip()) < 50:
         return "Error: Page content seems empty or protected."
    
    print(f"   ↳ 📝 Raw content length: {len(text)} characters")

    # 3. Compression / Résumé
    final_text = text
    if len(text) > 10000:
        print(f"   ↳ 🧠 Compressing content {source_type} ({len(text)} chars)...")
        try:
            final_text = summarize_raw_content(text)
            print(f"   ↳ 🧠 Compressed to {len(final_text)} characters.")
        except Exception as e:
            print(f"   ❌ Erreur compression: {e}")
            final_text = text[:10000] + "\n[Truncated due to error]"
        
    return f"""
<DOCUMENT_CONTENT>
<URL>{url}</URL>
<TYPE>{source_type}</TYPE>
<CONTENT>
{final_text}
</CONTENT>
</DOCUMENT_CONTENT>
"""