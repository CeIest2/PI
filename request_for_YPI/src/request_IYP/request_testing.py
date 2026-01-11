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

def execute_generated_queries(generation_result: Dict[str, Any]) -> Dict[str, Any]:
    URI = os.getenv("NEO4J_URI", "neo4j://iyp-bolt.ihr.live:7687")
    USER = os.getenv("NEO4J_USERNAME", "neo4j")
    PASSWORD = os.getenv("NEO4J_PASSWORD", "") 
    
    # 1. Vérification préliminaire
    if not generation_result.get("possible", False):
        return {
            "status": "SKIPPED",
            "user_intent": generation_result.get("user_intent", ""),
            "reason": generation_result.get("explanation", "Impossible request"),
            "results": []
        }

    queries = generation_result.get("queries", [])
    execution_report = {
        "status": "EXECUTED",
        "user_intent": generation_result.get("user_intent", ""),
        "total_queries": len(queries),
        "results": []
    }

    # 2. Connexion au Driver
    try:
        driver = GraphDatabase.driver(URI, auth=basic_auth(USER, PASSWORD))
        driver.verify_connectivity()
    except Exception as e:
        return {
            "status": "CONNECTION_ERROR",
            "error": f"Impossible de se connecter à Neo4j: {str(e)}",
            "results": []
        }

    # 3. Exécution des requêtes
    with driver.session() as session:
        for index, cypher_query in enumerate(queries):
            query_result = {
                "query_index": index + 1,
                "cypher": cypher_query,
                "success": False,
                "data": [],
                "error": None
            }
            
            try:
                # Exécution
                result = session.run(cypher_query)
                
                # Récupération et Nettoyage des données
                records = [record.data() for record in result]
                clean_data = serialize_neo4j_values(records)
                
                query_result["success"] = True
                query_result["data"] = clean_data
                query_result["count"] = len(clean_data)
                
            except Exception as e:
                query_result["success"] = False
                query_result["error"] = str(e)
            
            execution_report["results"].append(query_result)

    driver.close()

    """
    execution_report = {
        "status": "EXECUTED",
        "user_intent": generation_result.get("user_intent", ""),
        "total_queries": len(queries),
        "results": [....,....,....]
    }"""
    return execution_report

