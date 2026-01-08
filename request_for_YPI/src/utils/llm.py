# src/utils/llm.py
import os
from langchain_mistralai import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(mode_or_model: str = "smart"):
    """
    Renvoie le modèle Mistral configuré selon le mode demandé.
    
    MODES :
    - 'fast'      : Utilise mistral-small (Rapide, parfait pour le résumé/scraping).
    - 'smart'     : Utilise mistral-large (Polyvalent, pour la rédaction finale).
    - 'reasoning' : Utilise magistral (Le modèle de raisonnement avancé).
    """
    return get_llm_google(mode_or_model)
    # --- CONFIGURATION DES MODÈLES MISTRAL ---
    # Noms officiels de l'API Mistral
    MODEL_FAST = "mistral-small-latest"
    MODEL_SMART = "mistral-large-latest"
    MODEL_REASONING = "magistral-medium-2509" # Ou 'magistral-small-latest' selon votre accès
    
    # Récupération de la clé API
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("⚠️ Warning: MISTRAL_API_KEY introuvable dans les variables d'environnement.")

    print(f"🧠 [LLM Load] Mode: {mode_or_model}")

    # --- SÉLECTION DU MODÈLE ---
    
    if mode_or_model == "fast":
        return ChatMistralAI(
            model=MODEL_FAST,
            temperature=0,
            mistral_api_key=api_key
        )
        
    elif mode_or_model == "smart":
        return ChatMistralAI(
            model=MODEL_SMART,
            temperature=0.2, # Légère créativité pour la rédaction
            mistral_api_key=api_key
        )
        
    elif mode_or_model == "reasoning":
        print(f"   ↳ ✨ Activation du mode Raisonnement ({MODEL_REASONING})")
        return ChatMistralAI(
            model=MODEL_REASONING,
            temperature=0, # Température 0 recommandée pour les tâches logiques pures
            mistral_api_key=api_key
        )

    # Fallback : Si on passe un nom de modèle direct (ex: "open-mixtral-8x22b")
    else:
        return ChatMistralAI(
            model=mode_or_model,
            temperature=0,
            mistral_api_key=api_key
        )
    



def get_llm_google(mode_or_model: str = "smart", temperature: float = 0.2):
    """
    Factory pour récupérer le modèle Google Gemini.
    
    Args:
        mode_or_model: "fast", "smart", ou "reasoning".
        temperature: 0 pour le déterministe, 0.7 pour la créativité.
    """
    
    if mode_or_model == "fast":
        model_name = "gemini-2.5-flash-lite"
    elif mode_or_model in ["smart", "reasoning"]:
        model_name = "gemini-2.5-flash-lite"
    else:
        model_name = "gemini-2.5-flash-lite"


    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    return llm