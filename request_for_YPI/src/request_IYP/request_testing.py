import os
import json
from typing import Dict, Any, List
from neo4j import GraphDatabase, basic_auth





def serialize_neo4j_values(value):

    if hasattr(value, 'iso_format'): 
        return value.iso_format()
    if hasattr(value, 'to_native'): 
        return value.to_native()
    if isinstance(value, list):
        return [serialize_neo4j_values(v) for v in value]
    if isinstance(value, dict):
        return {k: serialize_neo4j_values(v) for k, v in value.items()}
    return value

def execute_cypher_test(cypher_query: str) -> Dict[str, Any]:
    """Exécute une seule requête Cypher et renvoie un rapport de succès/échec."""
    URI = os.getenv("NEO4J_URI", "neo4j://iyp-bolt.ihr.live:7687")
    USER = os.getenv("NEO4J_USERNAME", "neo4j")
    PASSWORD = os.getenv("NEO4J_PASSWORD", "") 
    
    query_result = {
        "cypher": cypher_query,
        "success": False,
        "data": [],
        "error": None,
        "count": 0
    }

    try:
        # Connexion et exécution
        driver = GraphDatabase.driver(URI, auth=basic_auth(USER, PASSWORD) if PASSWORD else None)
        with driver.session() as session:
            result = session.run(cypher_query)
            records = [record.data() for record in result]
            
            query_result["success"] = True
            query_result["data"] = serialize_neo4j_values(records)
            query_result["count"] = len(records)
        driver.close()
            
    except Exception as e:
        query_result["success"] = False
        query_result["error"] = str(e)
    
    return query_result

