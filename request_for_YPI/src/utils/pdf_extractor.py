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

# src/utils/pdf_extractor.py
import fitz  # PyMuPDF
import io
from typing import Optional

def is_pdf_url(url: str) -> bool:
    """Détection simple basée sur l'URL"""
    url_lower = url.lower()
    return url_lower.endswith('.pdf') or '/pdf/' in url_lower

def extract_text_from_pdf_bytes(pdf_bytes: bytes, max_chars: int = 500000) -> Optional[str]:
    """
    Extrait le texte d'un PDF déjà en mémoire (bytes).
    Plus fiable car ne nécessite pas de re-télécharger.
    """
    try:
        # On ouvre le PDF depuis la RAM
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            print(f"📄 [PDF] Chargé en mémoire: {doc.page_count} pages")
            
            extracted_text = []
            total_chars = 0
            
            for page in doc:
                if total_chars >= max_chars:
                    print(f"✂️ [PDF] Limite de {max_chars} caractères atteinte.")
                    break
                    
                text = page.get_text()
                extracted_text.append(text)
                total_chars += len(text)
        
        # Nettoyage basique
        full_text = "\n".join(extracted_text)
        return full_text[:max_chars]

    except Exception as e:
        print(f"❌ [PDF] Erreur lecture bytes: {e}")
        return None