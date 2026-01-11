# src/request_IYP/prompt_to_request.py
from src.request_IYP.generat_request import generate_cypher_for_request
from src.request_IYP.request_testing import execute_cypher_test
from src.request_IYP.analyse_results_request import analyse_research_result, analyze_and_correct_query
from src.request_IYP.probes_execution import execute_multiple_probes
from typing import Dict, Any

def process_user_request_with_retry(user_intent: str, max_retries: int = 5) -> Dict[str, Any]:
    print(f"🚀 [Pipeline] Début du traitement pour : '{user_intent}'")
    
    gen_result = generate_cypher_for_request(user_intent)

    current_queries  = gen_result.get("queries", [])
    current_query    = current_queries
    history          = []
    attempt          = 1
    probe_count      = 0
    max_probes       = 10
    research_context = ""

    while attempt <= max_retries:
        
        exec_res = execute_cypher_test(current_query)

        history.append({
            "attempt": attempt,
            "query": current_query,
            "success": exec_res.get("success"),
            "error": exec_res.get("error"),
            "count": exec_res.get("count", 0),
            "data_sample": exec_res.get("data") if exec_res.get("is_probe_execution") else exec_res.get("data", [])[:3]
        })
        
        analysis = analyze_and_correct_query({"user_intent": user_intent, "history": history})
        status = analysis.get("status")
        

        if analysis.get("corrected_query"):
            current_query = analysis["corrected_query"]

        if status == "VALID":
            print("✅ [Pipeline] Requête validée !")

            final_data = exec_res.get("data") if not exec_res.get("is_probe_execution") else []
            return {"status": "SUCCESS", "final_query": current_query, "data": final_data}
        
        elif status == "RESEARCH":
            if probe_count >= max_probes:
                print("🛑 [Pipeline] Trop d'enquêtes, passage en correction forcée.")
                status = "CORRECTED"
            else:
                print(f"🔍 [Pipeline] RESEARCH MODE : {analysis['message']}")
                compteur_reasearch += 1

                research_intent = analysis.get("correction", "Investigate the required information.")
                research_gen = generate_cypher_for_request(research_intent, research=True)
                
                if not research_gen.get("possible"):
                    print("❌ [Pipeline] Impossible de générer une requête pour la recherche.")
                    return {"status": "FAILED", "user_intent": user_intent, "history": history}
                
                results_research = execute_multiple_probes(research_gen.get("queries", ""))
                
                history.append({
                    "attempt": f"Research {compteur_reasearch}",
                    "query": research_gen.get("queries", ""),
                    "success": all(p["success"] for p in results_research),
                    "error": "\n".join([f"Sonde {i}: {p['error']}" for i, p in enumerate(results_research) if p['error']]),
                    "count": sum(p["count"] for p in results_research),
                    "data_sample": [p["data"] for p in results_research if p["data"]]
                })

                new_facts = analyse_research_result(results_research)
                research_context += new_facts

                print(f"🧠 [Pipeline] Nouvelle connaissance apprise : {new_facts}")
                
                gen_result = generate_cypher_for_request(user_intent, additional_context=research_context)
                continue

        if status == "CORRECTED":
            print(f"⚠️ [Pipeline] Correction suggérée : {analysis['message']}")
            is_probe_mode = False
            attempt += 1
        else:
            break

    return {"status": "FAILED", "user_intent": user_intent, "history": history}