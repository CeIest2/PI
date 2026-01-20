import fitz  # PyMuPDF
from typing import Optional

def is_pdf_url(url: str) -> bool:
    """
    Détermine si une URL pointe vers un PDF.
    """
    if not url:
        return False
    url_lower = url.lower()
    return url_lower.endswith('.pdf') or '/pdf/' in url_lower

def extract_text_from_pdf_bytes(pdf_bytes: bytes, max_chars: int = 500000) -> Optional[str]:
    """
    Extrait le texte d'un PDF déjà en mémoire (bytes).
    Plus fiable car ne nécessite pas de re-télécharger.
    """
    try:
        # On ouvre le PDF depuis la RAM via PyMuPDF
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            # print(f"📄 [PDF] Chargé en mémoire: {doc.page_count} pages") # (Optionnel : pour le debug)
            
            extracted_text = []
            total_chars = 0
            
            for page in doc:
                text = page.get_text()
                
                # Petite sécurité : si la page est vide (ex: image scannée), on ignore
                if not text.strip():
                    continue

                extracted_text.append(text)
                total_chars += len(text)

                if total_chars >= max_chars:
                    # print(f"✂️ [PDF] Limite de {max_chars} caractères atteinte.")
                    extracted_text.append("\n... [Tronqué par limite de taille] ...")
                    break
        
        full_text = "\n".join(extracted_text)
        return full_text

    except Exception as e:
        # On log l'erreur mais on ne crash pas l'app
        print(f"❌ [PDF Error] Impossible de lire les bytes: {str(e)}")
        return None