import json
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from pathlib import Path
import os

def evaluate_document_relevance(summarized_text: str, country: str, indicator_name: str, indicator_definition: str) -> dict:
    """
    Ask the LLM if the given texte is relevent for our purpose.
    """

    llm = get_llm(mode_or_model="fast")
    
    current_dir = Path(__file__).parent.parent.parent
    prompt_path = os.path.join(current_dir, "prompt", "evaluate_relevance.txt")

    prompt = ChatPromptTemplate.from_template(load_text_file(prompt_path))
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "country": country,
            "indicator_name": indicator_name,
            "indicator_definition": indicator_definition,
            "summarized_text": summarized_text[:50000]
        })
        
        content = response.content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)
        
        # Sécurité sur les clés
        if "decision" not in result:
            result["decision"] = "DISCARD"
            result["reason"] = "LLM parsing error (missing decision key)"
            
        return result

    except Exception as e:
        print(f"❌ Error evaluating relevance: {e}")
        return {"decision": "DISCARD", "reason": f"Error: {str(e)}"}