from src.request_IYP.generat_request import generate_cypher_for_request
from src.request_IYP.request_testing import execute_cypher_test
from src.request_IYP.analyse_results_request import analyze_and_correct_query
from typing import Dict, Any



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