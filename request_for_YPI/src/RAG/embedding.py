# src/utils/embeddings.py
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.utils.logger import logger

def get_embedding_model(task_type: str = "retrieval_document"):

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY manquante pour les embeddings.")
        return None

    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key,
        task_type=task_type 
    )

def get_text_embedding(text: str) -> list:
    """Génère le vecteur pour un texte donné (raccourci pour test)."""
    model = get_embedding_model(task_type="retrieval_document")
    try:
        return model.embed_query(text)
    except Exception as e:
        logger.error(f"Erreur embedding : {e}")
        return []