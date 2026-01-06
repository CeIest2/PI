# src/tools/neo4j.py
import os
from langchain_core.tools import tool
from neo4j import GraphDatabase
from src.utils.loaders import load_text_file
from src.utils.formatting import format_neo4j_results

# Configuration (à mettre dans .env)
URI = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH = None 

@tool
def run_infrastructure_query(query_file_path: str, country_code: str = "FR", asn: int = 16276, domain: str = "gouv.fr") -> str:
    """
    Exécute une requête Cypher stockée dans un fichier spécifique pour analyser l'infrastructure.
    
    Args:
        query_file_path: Le chemin relatif vers le fichier .cypher (ex: 'request_for_YPI/infrastructure/ixp_coverage/1.cypher')
        country_code: Code ISO du pays (ex: 'FR')
        asn: Numéro d'AS (ex: 16276)
        domain: Nom de domaine cible.
    """
    print(f"🔌 [Neo4j] Loading query from: {query_file_path}")
    
    try:
        # 1. Charger le contenu Cypher depuis le fichier
        cypher_query = load_text_file(query_file_path)
    except Exception as e:
        return f"❌ Erreur: Impossible de lire le fichier Cypher : {e}"

    params = {
        "countryCode": country_code,
        "hostingASN": asn,
        "domainName": domain
    }

    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            # 2. Exécution
            records, _, _ = driver.execute_query(cypher_query, parameters_=params)
            
            if not records:
                return "Aucun résultat trouvé dans la base de données."

            # 3. Formatage via votre système de templates YAML
            formatted_text = format_neo4j_results(records, query_file_path, params)
            return formatted_text
            
    except Exception as e:
        return f"Database Error: {str(e)}"