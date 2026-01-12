# src/request_IYP/analyse_results_request.py
import json
import re
import os
from typing import Dict, Any, List
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from src.utils.country_utils import load_country_mapping, apply_country_mapping
from src.utils.logger import logger

def clean_json_string(content: str) -> str:
    """Nettoie la chaîne de caractères pour ne garder que le JSON."""
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```', '', content)
    return content.strip()

def analyze_and_correct_query(execution_report: Dict[str, Any], mode: str = "smart", max_llm_retries: int = 2) -> Dict[str, Any]:
    """
    Analyse l'historique d'exécution et décide de la prochaine action.
    
    Args:
        execution_report: Dict contenant user_intent, history, additional_context
        mode: Mode LLM à utiliser
        max_llm_retries: Nombre de tentatives si le LLM ne fournit pas un JSON valide
    
    Returns:
        Dict avec status (VALID/CORRECTED/RESEARCH), message, et correction
    """
    llm = get_llm(mode)
    user_intent = execution_report.get("user_intent", "")
    history = execution_report.get("history", [])
    additional_context = execution_report.get("additional_context", "")
    
    if not history:
        logger.error("❌ [Analyse] Aucun historique à analyser")
        return {"status": "ERROR", "message": "Aucun historique à analyser"}

    # Construction de l'historique formaté
    history_str = ""
    for h in history:
        status_label = "✅ SUCCESS" if h['success'] else "❌ FAILED"
        rows = h.get('count', 0)
        
        # Gestion spéciale pour les entrées RESEARCH
        if isinstance(h.get('attempt'), str) and 'RESEARCH' in h['attempt']:
            history_str += f"""
[{h['attempt']}] RESEARCH PHASE
PROBES EXECUTED: {h['query']}
TOTAL ROWS: {rows}
---"""
        else:
            history_str += f"""
[Tentative {h['attempt']}] QUERY: {h['query']}
RESULTAT: {status_label} ({rows} lignes)
{f"ERREUR: {h['error']}" if h.get('error') else f"DATA SAMPLE: {json.dumps(h.get('data_sample', []), indent=2)}"}
---"""

    # Chargement du schéma et du prompt
    current_dir = Path(__file__).parent.parent.parent
    schema_path = os.path.join(current_dir, "prompt", "IYP_documentation.txt")
    schema_content = load_text_file(schema_path)
    
    system_prompt = load_text_file(os.path.join(current_dir, "prompt", "analyse_cypher_request_results.txt"))

    # Prompt humain amélioré avec contexte de recherche visible
    human_prompt = """
User Intent: {intent}

HISTORY OF ATTEMPTS:
{history_text}

RESEARCH CONTEXT (Knowledge acquired from previous investigations):
{research_context}

Based on this information, decide the next action.

REMINDER: You MUST provide a valid JSON response with these exact fields:
- "status": must be one of "VALID", "CORRECTED", or "RESEARCH"
- "explanation": string describing your reasoning
- "correction": 
  * For CORRECTED: a complete Cypher query
  * For RESEARCH: a specific, actionable investigation task (NOT "Investigate the required information")
  * For VALID: null

If status is RESEARCH, the correction field MUST contain a specific task like:
"Search for ASNs where org_name contains 'Google' to identify YouTube's infrastructure"
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    chain = prompt | llm
    
    logger.info("🧠 [Analyse] Appel au LLM pour décision...")
    
    # 🔧 FIX: Retry loop si le JSON est invalide
    for attempt in range(max_llm_retries):
        try:
            # Appel au LLM
            response = chain.invoke({
                "intent": user_intent,
                "history_text": history_str,
                "schema": schema_content,
                "additional_context": additional_context,
                "research_context": additional_context if additional_context else "None yet"
            })

            # Log du contenu brut pour debug
            if attempt > 0:
                logger.warning(f"🔄 [Analyse] Tentative LLM #{attempt + 1}")
            
            # 🔧 CRITICAL DEBUG: Afficher TOUTE la réponse
            print("\n" + "="*80)
            print("🔍 DEBUG: RÉPONSE COMPLÈTE DU LLM")
            print("="*80)
            print(response.content)
            print("="*80 + "\n")
            
            logger.debug(f"🤖 [Analyse] Réponse LLM brute (premiers 500 chars): {response.content[:500]}...")

            cleaned_content = clean_json_string(response.content)
            logger.debug(f"📄 [Analyse] Contenu JSON nettoyé: {cleaned_content[:300]}...")
            res_json = json.loads(cleaned_content)
            
            # Validation du JSON
            if "status" not in res_json:
                raise ValueError("Missing 'status' field in JSON")
            
            # 🔧 FIX: Le champ correction peut être absent ou explicitement null
            status = res_json.get("status")
            correction = res_json.get("correction", None)
            
            # 🔧 CRITICAL DEBUG
            print(f"\n🔍 Parsed JSON:")
            print(f"   Status: {status}")
            print(f"   Correction type: {type(correction)}")
            print(f"   Correction value: {correction}")
            print(f"   Correction is None: {correction is None}")
            print(f"   Correction is empty string: {correction == ''}")
            
            if status == "RESEARCH":
                if correction is None:
                    raise ValueError("Status is RESEARCH but correction field is null (None)")
                if isinstance(correction, str) and correction.strip() == "":
                    raise ValueError("Status is RESEARCH but correction field is empty string")
                # Si on arrive ici, correction contient du texte
                print(f"   ✅ RESEARCH intent validé: {correction[:100]}...")
            
            # Si on arrive ici, le JSON est valide
            print("   ✅ JSON validé avec succès\n")
            break
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"⚠️ [Analyse] Erreur validation JSON (tentative {attempt + 1}/{max_llm_retries}): {e}")
            
            if attempt == max_llm_retries - 1:
                # Dernière tentative échouée
                logger.error(f"❌ [Analyse] JSON invalide après {max_llm_retries} tentatives")
                logger.debug(f"Contenu brut final: {response.content[:800]}")
                return {
                    "status": "ERROR",
                    "message": f"LLM failed to provide valid JSON after {max_llm_retries} attempts: {str(e)}",
                    "corrected_query": None
                }
            
            # On continue le retry
            continue
    
    status = res_json.get("status", "CORRECTED")
    final_query = res_json.get("correction")
    
    # 🔧 DEBUG: Afficher ce qui a été extrait
    logger.debug(f"📊 [Analyse] Status extrait: {status}")
    logger.debug(f"📊 [Analyse] Correction extraite: {final_query[:200] if final_query else 'NULL/EMPTY'}")
    
    # 🔧 FIX: Vérifier que le champ correction n'est pas None/vide pour RESEARCH
    if status == "RESEARCH" and (not final_query or final_query.strip() == ""):
        logger.warning("⚠️ [Analyse] Status=RESEARCH mais correction vide/null!")
        logger.warning("   Le LLM n'a pas fourni d'intent de recherche exploitable")
        logger.debug(f"   JSON complet reçu: {json.dumps(res_json, indent=2)}")
        
        # On force un passage en mode CORRECTED pour éviter la boucle
        return {
            "status": "ERROR",
            "message": "RESEARCH status but no research intent provided by LLM",
            "corrected_query": None
        }
    
    # 🔧 FIX: Application du mapping pays uniquement pour CORRECTED
    if final_query and status == "CORRECTED":
        logger.debug("[Analyse] Application du mapping pays...")
        mapping = load_country_mapping()
        processed_queries = apply_country_mapping([final_query], mapping)
        final_query = processed_queries[0]
    
    # Pour RESEARCH, on laisse l'intent en langage naturel
    logger.success(f"✅ [Analyse] Décision: {status}")
    
    return {
        "status": status,
        "message": res_json.get("explanation"),
        "corrected_query": final_query
    }
    

def analyse_research_result(research_results: List[Dict[str, Any]], mode: str = "smart") -> str:
    """
    Analyse les résultats techniques d'une phase de RESEARCH pour en extraire 
    des faits concrets (clés existantes, labels trouvés, existence d'entités).
    
    Args:
        research_results: Liste de dicts avec les résultats des probes
        mode: Mode LLM à utiliser
    
    Returns:
        String contenant les faits découverts (Knowledge Note)
    """
    if not research_results:
        logger.warning("⚠️ [Research Analysis] Aucun résultat à analyser")
        return "Aucun résultat de recherche à analyser."

    llm = get_llm(mode)

    # Construction du résumé des données brutes
    raw_data_summary = ""
    for i, res in enumerate(research_results, start=1):
        status = "✅" if res.get("success") else "❌"
        raw_data_summary += f"""
[Probe {i}] 
Query: {res.get('query', 'N/A')}
Status: {status}
Rows: {res.get('count', 0)}
Sample Data: {json.dumps(res.get('data_sample', []), indent=2)}
Error: {res.get('error', 'None')}
---"""
    
    logger.debug(f"📊 [Research Analysis] Données à analyser:\n{raw_data_summary[:500]}...")
    
    # 🔧 FIX: Prompt amélioré pour analyse technique
    system_prompt = """You are a Technical Data Librarian specialized in graph databases.

Your job is to summarize technical findings from database probes into a concise "Knowledge Note".

RULES:
1. **Be EXTREMELY concise** (3-7 bullet points max).
2. **Focus ONLY on FACTS**: 
   - "Property X exists on relationship Y"
   - "Tag label 'Z' was found/not found"
   - "ASN 15169 belongs to Google"
   - "No data matches criteria X"
3. **If you find a property/label not in the official doc**, highlight it as: "⚠️ CORRECTION: Property 'abc' exists (not documented)"
4. **If a probe failed**, state clearly: "❌ Missing: Property/Label/Entity X"
5. **DO NOT write Cypher code**, only descriptive facts.
6. **Format**: Use bullet points with clear prefixes (✅ Found / ❌ Missing / ⚠️ Correction)

OUTPUT FORMAT:
Markdown list of factual findings.
"""

    human_prompt = """Analyze these database probe results and provide a concise technical summary:

{results}

Extract the key facts discovered or missing information identified."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    chain = prompt | llm

    logger.info("🔬 [Research Analysis] Extraction des connaissances...")
    
    try:
        response = chain.invoke({"results": raw_data_summary})
        analysis_text = response.content.strip()
        
        logger.success(f"✅ [Research Analysis] Analyse terminée ({len(analysis_text)} chars)")
        
        return f"\n{analysis_text}\n"
    
    except Exception as e:
        logger.error(f"❌ [Research Analysis] Erreur LLM: {e}")
        return f"\n⚠️ Research analysis failed: {str(e)}\n"