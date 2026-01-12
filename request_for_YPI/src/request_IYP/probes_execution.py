# src/request_IYP/probes_execution.py
import re
from typing import List, Dict, Any, Union
from src.request_IYP.request_testing import execute_cypher_test
from src.utils.logger import logger

def split_cypher_statements(query_text: str) -> List[str]:
    if not query_text or not isinstance(query_text, str):
        logger.warning(f"⚠️ [Splitting] Input invalide: {type(query_text)}")
        return []
    
    regex = r';(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)'
    statements = re.split(regex, str(query_text))
    
    clean_statements = [s.strip() for s in statements if s.strip()]
    # logger.info(f"✂️ [Splitting] {len(clean_statements)} requête(s) détectée(s)")
    return clean_statements


def execute_multiple_probes(query_input: Union[str, List[str]]) -> List[Dict[str, Any]]:

    # logger.info(f"🔬 [Probes] Début d'exécution - Type reçu: {type(query_input)}")
    
    if isinstance(query_input, str):
        # logger.debug(f"[Probes] Conversion string → list via split")
        queries_list = split_cypher_statements(query_input)
    elif isinstance(query_input, list):
        # logger.debug(f"[Probes] Format liste déjà correct")
        queries_list = query_input
    else:
        # logger.error(f"❌ [Probes] Type invalide: {type(query_input)}")
        return []
    
    if not queries_list:
        # logger.warning("⚠️ [Probes] Aucune requête à exécuter")
        return []
    
    # logger.info(f"📊 [Probes] {len(queries_list)} requête(s) à exécuter")
    
    probe_results = []
    
    for i, query in enumerate(queries_list, start=1):
        # logger.info(f"🔍 [Probe {i}/{len(queries_list)}] Exécution: {query[:80]}...")
        
        try:
            res = execute_cypher_test(query)
            
            probe_results.append({
                "probe_index": i,
                "query": query,
                "success": res["success"],
                "count": res["count"],
                "data_sample": res["data"][:3] if res["data"] else [],
                "error": res["error"]
            })
            
            status_icon = "✅" if res["success"] else "❌"
            # logger.info(f"{status_icon} [Probe {i}] Résultat: {res['count']} ligne(s)")
            
        except Exception as e:
            # logger.error(f"💥 [Probe {i}] Exception: {e}")
            probe_results.append({
                "probe_index": i,
                "query": query,
                "success": False,
                "count": 0,
                "data_sample": [],
                "error": str(e)
            })
    
    # logger.success(f"✅ [Probes] Terminé: {len(probe_results)} probe(s) exécutée(s)")
    return probe_results