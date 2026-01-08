import fitz  # PyMuPDF
import requests
from typing import Optional
import io


def is_pdf_url(url: str) -> bool:
    """
    Détermine si une URL pointe vers un PDF.
    
    Args:
        url: L'URL à vérifier
        
    Returns:
        True si l'URL semble pointer vers un PDF
    """
    url_lower = url.lower()
    return url_lower.endswith('.pdf') or '/pdf/' in url_lower


def extract_text_from_pdf_url(url: str, max_chars: int = 150000, timeout: int = 15) -> Optional[str]:
    """
    Télécharge et extrait le texte d'un PDF depuis une URL.
    
    Args:
        url: L'URL du fichier PDF
        max_chars: Nombre maximum de caractères à extraire (Défaut 150k)
        timeout: Timeout pour le téléchargement (secondes)
        
    Returns:
        Le texte extrait du PDF, ou None en cas d'erreur
    """
    try:
        print(f"📥 [PDF] Téléchargement du PDF depuis: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Vérification du Content-Type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
            print(f"⚠️ [PDF] Avertissement: Content-Type inattendu: {content_type}")
        

        pdf_content = io.BytesIO(response.content)
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        print(f"📄 [PDF] Document chargé: {doc.page_count} page(s)")
        
        extracted_text = []
        total_chars = 0
        
        for page_num in range(doc.page_count):
            if total_chars >= max_chars:
                print(f"✂️ [PDF] Limite de {max_chars} caractères atteinte à la page {page_num}")
                break
                
            page = doc[page_num]
            page_text = page.get_text()
            
            remaining_chars = max_chars - total_chars
            if len(page_text) > remaining_chars:
                page_text = page_text[:remaining_chars]
            
            extracted_text.append(page_text)
            total_chars += len(page_text)
        
        doc.close()
        
        full_text = '\n'.join(extracted_text)
        full_text = ' '.join(full_text.split())
        
        final_len = len(full_text)
        est_tokens = final_len // 4
        
        print(f"📊 [PDF Stats] Extraction réussie: {final_len} caractères (~{est_tokens} tokens)")
        
        return full_text[:max_chars]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ [PDF] Erreur de téléchargement: {e}")
        return None
    except fitz.FileDataError as e:
        print(f"❌ [PDF] Erreur: Fichier PDF corrompu ou invalide")
        return None
    except Exception as e:
        print(f"❌ [PDF] Erreur inattendue lors de l'extraction: {e}")
        return None


def extract_text_from_pdf_bytes(pdf_bytes: bytes, max_chars: int = 150000) -> Optional[str]:
    """
    Extrait le texte d'un PDF déjà en mémoire (bytes).
    
    Args:
        pdf_bytes: Le contenu du PDF en bytes
        max_chars: Nombre maximum de caractères à extraire
        
    Returns:
        Le texte extrait du PDF, ou None en cas d'erreur
    """
    try:
        pdf_stream = io.BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        
        extracted_text = []
        total_chars = 0
        
        for page_num in range(doc.page_count):
            if total_chars >= max_chars:
                break
                
            page = doc[page_num]
            page_text = page.get_text()
            
            remaining_chars = max_chars - total_chars
            if len(page_text) > remaining_chars:
                page_text = page_text[:remaining_chars]
            
            extracted_text.append(page_text)
            total_chars += len(page_text)
        
        doc.close()
        
        full_text = ' '.join(' '.join(extracted_text).split())
        return full_text[:max_chars]
        
    except Exception as e:
        print(f"❌ [PDF] Erreur lors de l'extraction depuis bytes: {e}")
        return None