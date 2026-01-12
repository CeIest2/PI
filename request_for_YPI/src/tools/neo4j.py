# src/tools/neo4j.py
import os
from langchain_core.tools import tool
from neo4j import GraphDatabase
from src.utils.loaders import load_text_file
from src.utils.formatting import format_neo4j_results
from pathlib import Path

# Configuration (à mettre dans .env)
URI = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH = None 




def fetch_indicator_data(indicator_path: Path, params: dict) -> str:
    """
    execution of the needed cypher files to get ground truth data from Neo4j 
    and formating results into a readable text block.

    return str: Formatted text block with all query results.
    """

    if not indicator_path.exists(): return f"   Error: Path not found {indicator_path}"

    cypher_files = sorted(indicator_path.glob("*.cypher"))
    
    if not cypher_files: return "No .cypher files found."

    aggregated_data = []
    print(f"Reading Neo4j data from: {indicator_path.name}")

    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            
            for cypher_file in cypher_files:
                query = load_text_file(str(cypher_file))
                
                # Execution
                records, _, _ = driver.execute_query(query, parameters_=params)
                
                # Formatting
                formatted_text = format_neo4j_results(records, str(cypher_file), params)
                aggregated_data.append(f"--- QUERY: {cypher_file.name} ---\n{formatted_text}")
                
    except Exception as e:
        return f"Critical DB Error: {e}"

    return "\n\n".join(aggregated_data)



