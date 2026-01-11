# src/request_IYP/probes_execution.py
import re
from typing import List, Dict, Any
from src.request_IYP.request_testing import execute_cypher_test

def split_cypher_statements(query_text: str) -> List[str]:
    """
    Découpe une chaîne de requêtes Cypher par point-virgule, 
    en ignorant les points-virgules à l'intérieur des guillemets.
    """
    # FIX: Regex corrigée pour ignorer les points-virgules entre quotes
    regex = r';(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)'
    statements = re.split(regex, str(query_text))
    
    clean_statements = [s.strip() for s in statements if s.strip()]
    print(f"DEBUG [Splitting] {len(clean_statements)} requêtes détectées.")
    return clean_statements

def execute_multiple_probes(query_input: Any) -> List[Dict[str, Any]]:
    """
    Prend une liste ou une chaîne de requêtes, les exécute séparément.
    """
    print(f" on print la liste de queries la {query_input}")   
    probe_results = [] 
    for i, q in enumerate(query_input):
        print(f"DEBUG [Exécution Sonde {i}] : {q[:100]}...")
        res = execute_cypher_test(q)
        probe_results.append({
            "query": q,
            "success": res["success"],
            "count": res["count"],
            "data_sample": res["data"][:3],
            "error": res["error"]
        })
    return probe_results