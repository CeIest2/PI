import json
import re
import os
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from pathlib import Path
from src.utils.loaders import load_text_file

def clean_json_string(content: str) -> str:
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```', '', content)
    return content.strip()

def generate_cypher_for_request(user_intent: str, mode: str = "smart") -> Dict[str, Any]:
    
    llm = get_llm(mode)
    
    current_dir = Path(__file__).parent.parent.parent
    iy_schema_content = load_text_file(os.path.join(current_dir, "prompt", "IYP_documentation.txt")) 
    system_prompt_request_generation = load_text_file(os.path.join(current_dir, "prompt", "cypher_request_generation.txt"))


    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_request_generation),
        ("human", "Request: {input}")
    ])
    
    chain = prompt | llm
    response_msg = chain.invoke({
        "input": user_intent,
        "schema": iy_schema_content 
    })
    
    content     = response_msg.content
    country_map = load_country_mapping()
    json_str    = clean_json_string(content)
    result      = json.loads(json_str)
    
    if result.get("possible") and result.get("queries"):
        result["queries"] = apply_country_mapping(result["queries"], country_map)
        
    return result
        




def load_country_mapping() -> Dict[str, str]:
    mapping = {}
    current_dir = Path(__file__).parent.parent.parent
    file_path = os.path.join(current_dir, "prompt", "country_code.txt")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "->" in line:
                name, code = line.split("->")
                mapping[name.strip().lower()] = code.strip()
    return mapping


def apply_country_mapping(queries: List[str], mapping: Dict[str, str]) -> List[str]:
    """Remplace __COUNTRY_Nom__ par le code ISO correspondant."""
    processed_queries = []
    for query in queries:
        matches = re.findall(r"__COUNTRY_(.+?)__", query)
        for country_name in matches:
            code = mapping.get(country_name.lower())
            placeholder = f"__COUNTRY_{country_name}__"
            if code:
                query = query.replace(placeholder, code)
            else:
                print(f"❌ [Mapping] Pays introuvable dans le fichier : {country_name}")
        processed_queries.append(query)
    return processed_queries




def main():
    # Test 1: Demande valide
    req1 = " Quels sont les plus gros points d'échange internet (IXP) au Japon ?"
    res1 = generate_cypher_for_request(req1)
    return res1

