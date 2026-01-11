# src/request_IYP/analyse_results_request.py
import json
import re
import os
from typing import Dict, Any, List
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
# Utilisation de country_utils comme dans ton import actuel
from src.utils.country_utils import load_country_mapping, apply_country_mapping

def clean_json_string(content: str) -> str:
    """Nettoie la chaîne de caractères pour ne garder que le JSON."""
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```', '', content)
    return content.strip()

def analyze_and_correct_query(execution_report: Dict[str, Any], mode: str = "smart") -> Dict[str, Any]:
    llm = get_llm(mode)
    user_intent = execution_report.get("user_intent", "")
    history = execution_report.get("history", [])
    
    if not history:
        return {"status": "ERROR", "message": "Aucun historique à analyser"}

    history_str = ""
    for h in history:
        status_label = "✅ SUCCESS" if h['success'] else "❌ FAILED"
        rows = h.get('count', 0)
        history_str += f"""
            [Tour {h['attempt']}] QUERY: {h['query']}
            RESULTAT: {status_label} ({rows} lignes)
            {f"ERREUR: {h['error']}" if h['error'] else f"DATA SAMPLE: {json.dumps(h.get('data_sample', []), indent=2)}"}
            ---"""

    current_dir = Path(__file__).parent.parent.parent
    schema_path = os.path.join(current_dir, "prompt", "IYP_documentation.txt")
    schema_content = load_text_file(schema_path)


    system_prompt = load_text_file(os.path.join(current_dir, "prompt", "analyse_cypher_request_results.txt"))

    human_prompt = """
    User Intent: {intent}
    
    HISTORY OF ATTEMPTS:
    {history_text}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    
    # 3. Appel au LLM
    response = chain.invoke({
        "intent": user_intent,
        "history_text": history_str,
        "schema": schema_content
    })

    res_json = json.loads(clean_json_string(response.content))
    status = res_json.get("status", "CORRECTED")
    
    final_query = res_json.get("correction")
    if final_query and status in ["CORRECTED", "RESEARCH"]:
        mapping = load_country_mapping()
        processed_queries = apply_country_mapping([final_query], mapping)
        final_query = processed_queries[0]

    return {
        "status": status,
        "message": res_json.get("explanation"),
        "corrected_query": final_query
    }
    

def analyse_research_result(research_results: List[Dict[str, Any]], mode: str = "smart") -> str:
    """
    Analyse les résultats techniques d'une phase de RESEARCH pour en extraire 
    des faits concrets (clés existantes, labels trouvés, existence d'entités).
    """
    if not research_results:
        return "Aucun résultat de recherche à analyser."

    llm = get_llm(mode)

    raw_data_summary = ""
    for i, res in enumerate(research_results):
        status = "✅" if res.get("success") else "❌"
        raw_data_summary += f"""
        [Sonde {i}] Query: {res.get('query')}
        Status: {status}
        Nb lignes: {res.get('count', 0)}
        Échantillon: {json.dumps(res.get('data_sample', []), indent=2)}
        ---"""
    print(f"DEBUG [Analyse Résultats Recherche]: {raw_data_summary}")
    # 2. Prompt d'analyse technique
    system_prompt = """You are a Technical Data Librarian. 
    Your job is to summarize technical findings from database probes into a short, concise "Knowledge Note".
    
    RULES:
    - Be extremely concise (3-5 bullet points max).
    - Focus ONLY on facts: "Property X exists", "Tag Y does not exist", "ASN for Google is 15169".
    - If you find a property not in the official doc, highlight it as a "Correction".
    - Do NOT write Cypher code, only descriptive facts.
    - If a probe failed or returned 0 rows, state it clearly as "Missing info".
    """

    human_prompt = """Analyze these database probe results and provide a concise technical summary:
    {results}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    chain = prompt | llm

    response = chain.invoke({"results": raw_data_summary})
    
    analysis_text = response.content.strip()
    
    return f"\n[TECHNICAL RESEARCH NOTE]:\n{analysis_text}\n"
