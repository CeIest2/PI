# src/utils/llm.py
import os
from langchain_mistralai import ChatMistralAI

def get_llm(mode_or_model: str = "smart"):
    """
    Renvoie le modèle Mistral configuré selon le mode demandé.
    
    MODES :
    - 'fast'      : Utilise mistral-small (Rapide, parfait pour le résumé/scraping).
    - 'smart'     : Utilise mistral-large (Polyvalent, pour la rédaction finale).
    - 'reasoning' : Utilise magistral (Le modèle de raisonnement avancé).
    """
    
    # --- CONFIGURATION DES MODÈLES MISTRAL ---
    # Noms officiels de l'API Mistral
    MODEL_FAST = "mistral-small-latest"
    MODEL_SMART = "mistral-large-latest"
    MODEL_REASONING = "magistral-medium-latest" # Ou 'magistral-small-latest' selon votre accès
    
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