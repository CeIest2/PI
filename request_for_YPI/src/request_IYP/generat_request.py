import json
import re
import os
from typing import Dict, List, Any
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from pathlib import Path
from src.utils.loaders import load_text_file
from src.request_IYP.analyse_results_request import analyze_and_correct_query
from src.request_IYP.request_testing import execute_cypher_test


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
    result["user_intent"] = user_intent
    
    if result.get("possible") and result.get("queries"):
        result["queries"] = apply_country_mapping(result["queries"], country_map)

    print(f"{result=}\n####")
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

def process_user_request_with_retry(user_intent: str, max_retries: int = 5) -> Dict[str, Any]:
    """
    Pipeline complet : Génération -> Test -> Analyse/Correction (Loop)
    """
    print(f"🚀 [Pipeline] Début du traitement pour : '{user_intent}'")
    
    # 1. Génération initiale
    gen_result = generate_cypher_for_request(user_intent)
    
    if not gen_result.get("possible"):
        print("❌ [Pipeline] Requête jugée impossible dès le départ.")
        return gen_result


    current_query = gen_result["queries"][0]
    
    attempt = 1
    while attempt <= max_retries:
        print(f"🔄 [Pipeline] Tentative {attempt}/{max_retries}")
        
        exec_res = execute_cypher_test(current_query)
        
        report = {
            "user_intent": user_intent,
            "results": [exec_res]
        }
        
        analysis = analyze_and_correct_query(report)
        
        if analysis["status"] == "VALID":
            print("✅ [Pipeline] Requête validée par l'analyste !")
            return {
                "status": "SUCCESS",
                "final_query": current_query,
                "explanation": analysis["message"],
                "attempts": attempt,
                "data_sample": exec_res["data"][:3] 
            }
        
        elif analysis["status"] == "CORRECTED":
            print(f"⚠️ [Pipeline] Correction nécessaire : {analysis['message']}")
            current_query = analysis["corrected_query"]
            if not current_query:
                break # On ne peut plus corriger
            attempt += 1
        
        else:
            print(f"❌ [Pipeline] Erreur critique lors de l'analyse.")
            break

    return {
        "status": "FAILED",
        "message": f"Impossible de générer une requête valide après {max_retries} tentatives.",
        "user_intent": user_intent
    }


def main():
    # Test 1: Demande valide
    req1 = " Quels sont les plus gros points d'échange internet (IXP) au Japon ?"

    return process_user_request_with_retry(req1)