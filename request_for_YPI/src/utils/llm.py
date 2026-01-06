# src/utils/llm.py
import os
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

load_dotenv()

# Définition de vos profils de modèles
MODELS_MAPPING = {
    "fast": "mistral-small-latest",
    "smart": "mistral-large-latest",
    # Vous pouvez ajouter d'autres variantes ici
    "creative": "codestral-latest" 
}

def get_llm(mode_or_model: str = "smart", temperature: float = 0):
    """
    Récupère le modèle selon un mode ('fast', 'smart') ou un nom direct.
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is missing")

    # Si l'utilisateur passe "fast", on prend le modèle associé, sinon on utilise la chaîne telle quelle
    model_name = MODELS_MAPPING.get(mode_or_model, mode_or_model)
    
    print(f"🧠 [LLM Load] Using model: {model_name}")

    return ChatMistralAI(
        model=model_name,
        api_key=api_key,
        temperature=temperature
    )