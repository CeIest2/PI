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
    return clean_statements


def execute_multiple_probes(query_input: Union[str, List[str]]) -> List[Dict[str, Any]]:

    
    if isinstance(query_input, str):
        queries_list = split_cypher_statements(query_input)
    elif isinstance(query_input, list):
        queries_list = query_input
    else:
        return []
    
    if not queries_list:
        return []
    
    
    probe_results = []
    
    for i, query in enumerate(queries_list, start=1):
        
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
            
            
        except Exception as e:
            probe_results.append({
                "probe_index": i,
                "query": query,
                "success": False,
                "count": 0,
                "data_sample": [],
                "error": str(e)
            })
    
    return probe_results