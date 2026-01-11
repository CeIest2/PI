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

    # 2. Système de prompt "Auditeur & Enquêteur"
    system_prompt = """You are a Skeptical Senior Data Auditor & Investigator for a graph database.
    
    STRICT SCHEMA:
    {schema}
    
    YOUR MISSION:
    Analyze the HISTORY of attempts to reach the User Intent. You must decide if the last query is VALID, 
    if it needs a logical CORRECTION, or if you need to PROBE (explore) the database.

    AUDIT STEPS (Mandatory):
    1. LOGICAL VOLUME: If the intent is to "List/Find" and the result is 0 rows, it is a FAILURE.
    2. SYNTHESIS: If a previous PROBE revealed a key or relationship type (e.g., 'CENSORED'), you MUST use it in your next correction.
    3. DIRECTION CHECK: Ensure relationship directions (A)-[:REL]->(B) match the schema meaning.

    DECISION STRATEGY (status):
    - "VALID": The query is perfect and returns relevant data.
    - "CORRECTED": You are 100% sure of the fix based on the schema or previous probes.
    - "PROBE": You are unsure why it returns 0 rows or errors. Generate an exploration query.
      Examples: "MATCH (n:AS) RETURN keys(n) LIMIT 1" or "MATCH ()-[r]->() RETURN type(r) LIMIT 5".

    CRITICAL RULES:
    - ONE STATEMENT ONLY: Never use semicolons (;). Generate EXACTLY ONE Cypher statement.
    - NO REPETITION: Do not suggest a query that has already failed in the history.
    - NO HALLUCINATION: If a property is not in the schema, PROBE it before using it.
    - NEVER use UNION to test multiple hypotheses. It causes schema mismatch errors. If you are unsure, use the PROBE status with multiple queries separated by semicolons (;).
    OUTPUT FORMAT (JSON):
    {{
        "status": "VALID" | "CORRECTED" | "PROBE",
        "explanation": "Briefly explain your reasoning based on the history.",
        "correction": "The Cypher query (null if status is VALID)"
    }}
    """

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
    
    try:
        res_json = json.loads(clean_json_string(response.content))
        status = res_json.get("status", "CORRECTED")
        
        final_query = res_json.get("correction")
        if final_query and status in ["CORRECTED", "PROBE"]:
            mapping = load_country_mapping()
            processed_queries = apply_country_mapping([final_query], mapping)
            final_query = processed_queries[0]

        return {
            "status": status,
            "message": res_json.get("explanation"),
            "corrected_query": final_query
        }
        
    except Exception as e:
        return {
            "status": "ERROR", 
            "message": f"Echec de l'analyse LLM: {str(e)}",
            "corrected_query": None
        }