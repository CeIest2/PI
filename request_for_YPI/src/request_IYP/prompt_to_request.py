# src/request_IYP/prompt_to_request.py
from src.request_IYP.generat_request import generate_cypher_for_request
from src.request_IYP.request_testing import execute_cypher_test
from src.request_IYP.analyse_results_request import analyze_and_correct_query
from typing import Dict, Any

def process_user_request_with_retry(user_intent: str, max_retries: int = 5) -> Dict[str, Any]:
    print(f"🚀 [Pipeline] Début du traitement pour : '{user_intent}'")
    
    gen_result = generate_cypher_for_request(user_intent)
    if not gen_result.get("possible"): return gen_result

    current_query = gen_result["queries"]
    history = []
    attempt = 1
    probe_count = 0
    max_probes = 10

    while attempt <= max_retries:
        print(f"🔄 [Pipeline] {'[ENQUÊTE]' if probe_count > 0 else ''} Tentative {attempt}/{max_retries}")
        
        exec_res = execute_cypher_test(current_query)
        history.append({
            "attempt": attempt,
            "query": current_query,
            "success": exec_res.get("success"),
            "error": exec_res.get("error"),
            "count": exec_res.get("count", 0),
            "data_sample": exec_res.get("data", [])[:3]
        })
        
        analysis = analyze_and_correct_query({"user_intent": user_intent, "history": history})
        
        status = analysis.get("status")
        
        if status == "VALID":
            print("✅ [Pipeline] Requête validée !")
            return {"status": "SUCCESS", "final_query": current_query, "data": exec_res.get("data")}
        
        elif status == "PROBE":
            if probe_count >= max_probes:
                print("🛑 [Pipeline] Trop d'enquêtes effectuées, on tente une correction finale.")
                status = "CORRECTED"
            else:
                print(f"🔍 [Pipeline] L'agent enquête : {analysis['message']}")
                current_query = analysis["corrected_query"]
                probe_count += 1
                continue # On relance sans incrémenter 'attempt'

        if status == "CORRECTED":
            print(f"⚠️ [Pipeline] Correction suggérée : {analysis['message']}")
            current_query = analysis["corrected_query"]
            attempt += 1
        else:
            break

    return {"status": "FAILED", "user_intent": user_intent, "history": history}