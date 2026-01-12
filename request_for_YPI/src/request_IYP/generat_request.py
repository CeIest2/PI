import json
import re
import os
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from pathlib import Path
from src.utils.loaders import load_text_file
from src.utils.country_utils import load_country_mapping, apply_country_mapping

def clean_json_string(content: str) -> str:
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```', '', content)
    return content.strip()

def generate_cypher_for_request(user_intent: str, mode: str = "smart", research: bool = False, additional_context: str = "") -> Dict[str, Any]:
    llm = get_llm(mode)
    
    current_dir = Path(__file__).parent.parent.parent
    iy_schema_content = load_text_file(os.path.join(current_dir, "prompt", "IYP", "IYP_documentation.txt")) 
    
    if research:
        system_prompt_request_generation = load_text_file(os.path.join(current_dir, "prompt", "IYP", "cypher_request_research_generation.txt"))
    else:
        system_prompt_request_generation = load_text_file(os.path.join(current_dir, "prompt", "IYP", "cypher_request_generation.txt"))

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_request_generation),
        ("human", "Request: {input}")
    ])
    
    chain = prompt | llm
    response_msg = chain.invoke({
        "input": user_intent,
        "schema": iy_schema_content,
        "additional_context": additional_context
    })
    
    content     = response_msg.content
    country_map = load_country_mapping()
    json_str    = clean_json_string(content)
    result      = json.loads(json_str)
    result["user_intent"] = user_intent
    
    # 🔧 FIX CRITIQUE: Application du mapping pays
    if result.get("possible") and result.get("queries"):
        queries = result["queries"]
        
        if isinstance(queries, str):
            mapped = apply_country_mapping([queries], country_map)
            result["queries"] = mapped[0]  # On récupère la string mappée
        
        elif isinstance(queries, list):
            result["queries"] = apply_country_mapping(queries, country_map)

    return result