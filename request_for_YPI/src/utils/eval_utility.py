import json
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from pathlib import Path
import os

def evaluate_document_relevance(summarized_text: str, country: str, indicator_name: str, indicator_definition: str) -> dict:
    """
    Ask the LLM if the summarized text is relevant for the final report.
    Returns a dict: {"decision": "KEEP"|"DISCARD", "reason": "...", "confidence": int}
    """

    llm = get_llm(mode_or_model="fast")
    
    current_dir = Path(__file__).parent.parent.parent # Ajustez selon où vous mettez cette fonction
    prompt_path = os.path.join(current_dir, "prompt", "evaluate_relevance.txt")


    try:
        # Assurez-vous d'avoir load_text_file importé ou utilisez open()
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
    except FileNotFoundError:
        print(f"⚠️ Prompt file not found at {prompt_path}, using fallback.")
        template = """
        Evaluate relevance for {indicator_name} in {country}.
        Doc: {summarized_text}
        Return JSON {{ "decision": "KEEP" or "DISCARD", "reason": "..." }}
        """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "country": country,
            "indicator_name": indicator_name,
            "indicator_definition": indicator_definition,
            "summarized_text": summarized_text[:50000] # On limite pour éviter les erreurs de contexte
        })
        
        # Nettoyage bourrin du JSON (au cas où le LLM ajoute ```json ... ```)
        content = response.content.replace("```json", "").replace("```", "").strip()
        
        # Parsing
        result = json.loads(content)
        
        # Sécurité sur les clés
        if "decision" not in result:
            result["decision"] = "DISCARD"
            result["reason"] = "LLM parsing error (missing decision key)"
            
        return result

    except Exception as e:
        print(f"❌ Error evaluating relevance: {e}")
        # En cas d'erreur, on rejette par sécurité (ou on garde, selon votre tolérance au bruit)
        return {"decision": "DISCARD", "reason": f"Error: {str(e)}", "confidence_score": 0}