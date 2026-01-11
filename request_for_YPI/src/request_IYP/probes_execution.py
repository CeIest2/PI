import re
from typing import List, Dict, Any
from src.request_IYP.request_testing import execute_cypher_test

def split_cypher_statements(query_text: str) -> List[str]:
    """
    Découpe une chaîne de requêtes Cypher par point-virgule, 
    en ignorant les points-virgules à l'intérieur des guillemets.
    """
    statements = re.split(r';(?=(?:[^\'"]*[\'"][^\' Res]*[\'"])*[^\' Res]*$)', query_text)
    return [s.strip() for s in statements if s.strip()]

def execute_multiple_probes(query_input: Any) -> List[Dict[str, Any]]:
    """
    Prend une liste ou une chaîne de requêtes, les exécute séparément
    et retourne un historique détaillé des résultats.
    """
    queries = split_cypher_statements(query_input)
    probe_results = []
    
    for q in queries:
        res = execute_cypher_test(q)
        probe_results.append({
            "query": q,
            "success": res["success"],
            "count": res["count"],
            "data_sample": res["data"][:3],
            "error": res["error"]
        })
    return probe_results