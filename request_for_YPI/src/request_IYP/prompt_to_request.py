# src/request_IYP/prompt_to_request.py
from src.request_IYP.generat_request import generate_cypher_for_request
from src.request_IYP.request_testing import execute_cypher_test
from src.request_IYP.analyse_results_request import analyse_research_result, analyze_and_correct_query
from src.request_IYP.probes_execution import execute_multiple_probes
from src.utils.logger import logger
from typing import Dict, Any

def process_user_request_with_retry(user_intent: str, max_retries: int = 6, logger_active: bool = False) -> Dict[str, Any]:
    """
    Pipeline principal avec gestion du mode RESEARCH.
    
    Args:
        user_intent: Requête utilisateur en langage naturel
        max_retries: Nombre maximum de tentatives de correction
    
    Returns:
        Dictionnaire avec le statut final et les données
    """
    if logger_active :logger.section(f"Pipeline de traitement")
    if logger_active :logger.info(f"📝 Intent: '{user_intent}'")
    
    attempt = 1
    probe_count = 0
    max_probes = 8
    
    gen_result = generate_cypher_for_request(user_intent)
    
    if not gen_result.get("possible"):
        if logger_active :logger.error("❌ [Pipeline] Requête impossible à traduire en Cypher")
        return {"status": "IMPOSSIBLE", "message": gen_result.get("explanation")}
    
    # Gestion robuste du format de requête initiale
    current_queries = gen_result.get("queries", [])
    if isinstance(current_queries, list):
        current_query = current_queries[0] if current_queries else ""
    else:
        current_query = current_queries
    
    history = []
    research_context = ""
    
    if logger_active :logger.info(f"🎯 [Pipeline] Requête initiale générée")
    if logger_active :logger.debug(f"   Query: {current_query[:100]}...")
    
    while attempt <= max_retries:
        if logger_active :logger.info(f"🔄 [Tentative {attempt}/{max_retries}]")
        
        exec_res = execute_cypher_test(current_query)
        
        # Stockage dans l'historique
        history.append({
            "attempt": attempt,
            "query": current_query,
            "success": exec_res.get("success"),
            "error": exec_res.get("error"),
            "count": exec_res.get("count", 0),
            "data_sample": exec_res.get("data", [])[:3]
        })
        
        # Affichage du résultat de l'exécution
        if exec_res.get("success"):
            if logger_active :logger.success(f"✅ [Tentative {attempt}] Succès: {exec_res.get('count', 0)} ligne(s)")
            pass
        else:
            if logger_active :logger.warning(f"⚠️ [Tentative {attempt}] Échec: {exec_res.get('error', 'Unknown error')[:100]}...")
            
            
        effective_context = research_context
        if probe_count >= max_probes:
            limit_warning = "\n\n[SYSTEM NOTICE: RESEARCH LIMIT REACHED. DO NOT request more research probes. You MUST provide a final 'CORRECTED' Cypher query or mark the status as 'VALID' based on available info.]"
            effective_context += limit_warning
        analysis = analyze_and_correct_query({
            "user_intent": user_intent, 
            "history": history,
            "additional_context": effective_context
        })
        
        status = analysis.get("status")
        if logger_active :logger.info(f"🧠 [Analyse] Statut: {status}")
        if logger_active :logger.info(f"💡 [Analyse] Explication: {analysis.get('message', 'N/A')[:200]}...")
        
        # === DÉCISIONS STRATÉGIQUES ===
        
        if status == "VALID":
            if logger_active :logger.success("✅ [Pipeline] Requête VALIDÉE !")
            final_data = exec_res.get("data", [])
            return {
                "status": "SUCCESS", 
                "final_query": current_query, 
                "data": final_data,
                "attempts": attempt,
                "research_cycles": probe_count
            }
        
        elif status == "RESEARCH":
            probe_count += 1
            
            if probe_count > max_probes:
                if logger_active :logger.warning(f"🛑 [Pipeline] Limite de {max_probes} recherches atteinte")
                
                if analysis.get("corrected_query"):
                    if logger_active :logger.info("🔄 [Pipeline] Application de la dernière correction disponible")
                    current_query = analysis["corrected_query"]
                    attempt += 1
                    continue
                else:
                    if logger_active :logger.error("❌ [Pipeline] Aucune correction disponible après limite RESEARCH")
                    return {
                        "status": "FAILED",
                        "user_intent": user_intent,
                        "history": history,
                        "reason": "Max research probes reached without valid correction",
                        "attempts": attempt,
                        "research_cycles": probe_count
                    }
            
            if logger_active :logger.section(f"Research Mode (Probe {probe_count}/{max_probes})")
            
            research_intent = analysis.get("corrected_query", "")
            
            if not research_intent or research_intent.strip() == "":
                if logger_active :logger.error("❌ [Research] Intent vide reçu de l'analyse")
                if logger_active :logger.debug(f"   Analysis dict: {analysis}")
                attempt += 1
                continue
            
            vague_patterns = ["investigate the required", "investigate required", "check the data", "find out more"]
            if any(pattern in research_intent.lower() for pattern in vague_patterns):
                if logger_active :logger.warning(f"⚠️ [Research] Intent trop vague détecté: '{research_intent[:100]}'")
                if logger_active :logger.info("🔄 [Pipeline] Forçage d'une correction directe...")
                
                # On force une correction avec le contexte actuel
                if analysis.get("message"):
                    # On essaie de générer une requête avec l'explication fournie
                    if logger_active :logger.info("   Tentative de génération basée sur l'explication...")
                    gen_result = generate_cypher_for_request(
                        user_intent + " - Context: " + analysis.get("message", ""),
                        additional_context=research_context
                    )
                    if gen_result.get("possible") and gen_result.get("queries"):
                        new_queries = gen_result["queries"]
                        current_query = new_queries[0] if isinstance(new_queries, list) else new_queries
                        logger.success("✅ Nouvelle requête générée avec contexte")
                        attempt += 1
                        continue
                
                # Si rien ne fonctionne, on passe à la tentative suivante
                attempt += 1
                continue
            
            if logger_active :logger.info(f"🔍 [Research] Intent: {research_intent[:150]}...")
            
            # Génération des requêtes de recherche
            research_gen = generate_cypher_for_request(
                research_intent, 
                research=True,
                additional_context=research_context
            )
            
            if not research_gen.get("possible"):
                if logger_active :logger.error("❌ [Research] Impossible de générer des probes")
                if logger_active :logger.info("🔄 [Pipeline] Tentative de correction directe...")
                attempt += 1
                continue
            
            research_queries = research_gen.get("queries", "")
            
            if isinstance(research_queries, list):
                if research_queries and isinstance(research_queries[0], str) and len(research_queries[0]) == 1:
                    if logger_active :logger.warning("⚠️ [Research] Queries reçues comme liste de caractères, reconstruction...")
                    research_queries = "".join(research_queries)
                else:
                    research_queries = "; ".join(research_queries)
            
            if not research_queries or (isinstance(research_queries, str) and research_queries.strip() == ""):
                # logger.warning("⚠️ [Research] Queries vides générées")
                attempt += 1
                continue
            
            if logger_active :logger.info(f"📋 [Research] Format reçu: {type(research_queries)}")
            if logger_active :logger.debug(f"   Queries: {research_queries[:150]}...")
            
            # Exécution des probes
            results_research = execute_multiple_probes(research_queries)
            
            if not results_research:
                if logger_active :logger.warning("⚠️ [Research] Aucun résultat de probe")
                attempt += 1
                continue
            
            # Historique amélioré pour RESEARCH
            successful_probes = sum(1 for p in results_research if p["success"])
            total_rows = sum(p["count"] for p in results_research)
            
            # logger.info(f"📊 [Research] {successful_probes}/{len(results_research)} probes réussies")
            # logger.info(f"📊 [Research] {total_rows} lignes totales récupérées")
            
            history.append({
                "attempt": f"{attempt}-RESEARCH-{probe_count}",
                "query": f"[{len(results_research)} probes exécutées]",
                "success": successful_probes > 0,
                "error": None,
                "count": total_rows,
                "data_sample": [p["data_sample"] for p in results_research if p["data_sample"]],
                "research_details": results_research
            })
            
            # Analyse des résultats RESEARCH
            if logger_active :logger.info("🧠 [Research] Analyse des découvertes...")
            new_facts = analyse_research_result(results_research)
            
            # Gestion propre du contexte de recherche
            if new_facts and new_facts.strip():
                research_context += f"\n\n--- RESEARCH #{probe_count} ---\n{new_facts}"
                if logger_active :logger.success(f"🧠 [Research] Nouvelles connaissances acquises:")
                if logger_active :logger.info(f"   {new_facts[:200]}...")
            else:
                if logger_active :logger.warning("⚠️ [Research] Aucune nouvelle information extraite")
            
            # Régénération avec le contexte enrichi
            if logger_active :logger.info("🔄 [Research] Régénération de la requête principale avec contexte enrichi...")
            gen_result = generate_cypher_for_request(
                user_intent, 
                additional_context=research_context
            )
            
            if gen_result.get("possible") and gen_result.get("queries"):
                new_queries = gen_result["queries"]
                if isinstance(new_queries, list):
                    current_query = new_queries[0] if new_queries else current_query
                else:
                    current_query = new_queries
                if logger_active :logger.success("✅ [Research] Requête principale mise à jour")
                if logger_active :logger.debug(f"   New Query: {current_query[:100]}...")
            else:
                if logger_active :logger.error("❌ [Research] Échec de régénération")
                attempt += 1
                continue
            
            # On ne fait PAS attempt += 1 ici car ce n'est pas une vraie tentative
            if logger_active :logger.info("🔄 [Research] Retour au pipeline principal avec nouvelle requête")
            continue
        
        elif status == "CORRECTED":
            # 🔧 FIX: Mise à jour de la requête avant d'incrémenter
            if analysis.get("corrected_query"):
                current_query = analysis["corrected_query"]
                if logger_active :logger.info(f"🔧 [Pipeline] Correction appliquée, nouvelle tentative")
            else:
                if logger_active :logger.warning("⚠️ [Pipeline] Statut CORRECTED mais pas de requête fournie")
                pass
            
            attempt += 1
            continue
        
        else:
            # Statut inconnu ou ERROR
            # logger.warning(f"⚠️ [Pipeline] Statut inconnu ou erreur: {status}")
            attempt += 1
    
    # Échec après max_retries
    if logger_active :logger.error(f"❌ [Pipeline] Échec après {max_retries} tentatives")
    return {
        "status": "FAILED", 
        "user_intent": user_intent, 
        "history": history,
        "attempts": attempt - 1,
        "research_cycles": probe_count,
        "reason": "Max retries reached"
    }