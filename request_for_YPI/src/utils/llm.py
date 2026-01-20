# src/utils/llm.py
import os
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(mode_or_model: str = "smart"):
    return get_llm_google(mode_or_model)


def get_llm_google(mode_or_model: str = "smart", temperature: float = 0.2):
    """
    Factory pour récupérer le modèle Google Gemini.
    
    Args:
        mode_or_model: "fast", "smart", "reasoning", ou "report_redaction"
        temperature: 0 pour le déterministe, 0.7 pour la créativité
    """
    
    if mode_or_model == "fast":
        model_name = "gemini-2.5-flash-lite"
        temperature = 0
    elif mode_or_model == "smart":
        # 🔧 FIX: Utiliser un modèle plus puissant pour l'analyse
        model_name = "gemini-2.5-flash-lite"
        temperature = 0.1
    elif mode_or_model == "reasoning":
        model_name = "gemini-2.0-flash-thinking-exp"
        temperature = 0
    elif mode_or_model == "report_redaction":
        model_name = "gemini-3-flash-preview"
        temperature = 0.3
    else:
        # Fallback
        model_name = "gemini-2.5-flash-lite"
        temperature = 0.2

    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        return llm
    except Exception as e:
        print(f"❌ Erreur lors du chargement du modèle {model_name}: {e}")
        # Fallback vers un modèle de base
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.2,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )