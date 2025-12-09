from mistralai import Mistral
import os




# function to call a llm and output the respond

import os
from mistralai import Mistral

# Assure-toi d'avoir installé le package : pip install mistralai

def llm_call_respond(prompt: str, thinking: bool = True) -> str:

    
    # 1. Vérification de la Clé API
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("❌ Erreur : La variable d'environnement MISTRAL_API_KEY n'est pas définie.")
        return "Erreur : Pas de clé API trouvée."
    
    client = Mistral(api_key=api_key)

    if thinking:
        models_candidates = [
            "magistral-medium-latest", 
            "magistral-small-latest"
        ]
    else:
        models_candidates = [
            "mistral-large-latest",
            "mistral-large-2512",
            "mistral-large-2411",
            "mistral-medium-latest"
        ]

    last_error = None
    
    for model in models_candidates:
        print(f"🔄 Tentative avec le modèle : {model}...")
        
        try:
            response = client.chat.complete(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            print(f"✅ Succès ! Modèle utilisé : {model}")
            raw_content = response.choices[0].message.content
            print("####")
            print("#####")
            print(f"💬 Contenu brut reçu : {raw_content}...")
            print("####")
            print("#####")
            # Si le contenu est une liste (Cas des modèles avec Reasoning)
            if isinstance(raw_content, list):
                final_text = ""
                for chunk in raw_content:
                    # On vérifie si le chunk est de type 'text'
                    # (On ignore les 'thinking' ou 'reasoning')
                    if hasattr(chunk, 'type') and chunk.type == 'text':
                        final_text += chunk.text
                return final_text
            
        except Exception as e:
            print(f"⚠️ Échec avec {model}. Raison : {e}")
            last_error = e
            continue # Passe au modèle suivant dans la liste

    error_msg = f"❌ Tous les modèles ont échoué. Dernière erreur : {last_error}"
    print(error_msg)
    return error_msg
        


if __name__ == "__main__":
    test_prompt = "Explique la théorie de la relativité en termes simples."
    response = llm_call_respond(test_prompt, thinking=False)
    print("\n💬 Réponse du LLM :")
    print(response)