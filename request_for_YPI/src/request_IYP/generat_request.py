import json
import re
import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from pathlib import Path
from src.utils.loaders import load_text_file
from src.utils.country_utils import load_country_mapping, apply_country_mapping
from src.utils.logger import logger # Correction de l'import logger

def clean_and_parse_json(content: str) -> Dict[str, Any]:
    """Nettoie et répare le JSON du LLM de manière robuste."""
    json_str = re.sub(r'```json\s*|```\s*', '', content).strip()
    
    if json_str.count('"') % 2 != 0:
        json_str += '"'
    if not json_str.endswith('}'):
        json_str += '}'

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON malformé détecté : {e}")
        last_brace = json_str.rfind('}')
        if last_brace != -1:
            try:
                return json.loads(json_str[:last_brace+1])
            except: pass
        
        return {
            "possible": False, 
            "explanation": f"JSON Error: {str(e)}",
            "queries": []
        }

def generate_cypher_for_request(user_intent: str, mode: str = "smart", research: bool = False, additional_context: str = "") -> Dict[str, Any]:
    llm = get_llm(mode)
    
    current_dir = Path(__file__).parent.parent.parent
    iy_schema_content = load_text_file(os.path.join(current_dir, "prompt", "IYP", "IYP_documentation.txt")) 
    
    prompt_file = "cypher_request_research_generation.txt" if research else "cypher_request_generation.txt"
    system_prompt = load_text_file(os.path.join(current_dir, "prompt", "IYP", prompt_file))

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Request: {input}")
    ])

    chain = prompt | llm

    response_msg = chain.invoke({
        "input": user_intent,
        "schema": iy_schema_content,
        "country_code": "KZ",
        "additional_context": additional_context
    })
    
    result = clean_and_parse_json(response_msg.content)
    result["user_intent"] = user_intent
    
    if result.get("possible") and result.get("queries"):
        country_map = load_country_mapping()
        queries = result["queries"]
        
        if isinstance(queries, str):
            mapped = apply_country_mapping([queries], country_map)
            result["queries"] = mapped[0]
        elif isinstance(queries, list):
            result["queries"] = apply_country_mapping(queries, country_map)
            
    return result