import argparse
import sys
import os
from dotenv import load_dotenv
from pathlib import Path
from neo4j import GraphDatabase

# Import de votre graphe LangChain
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"
from src.agents.graph import graph
from langchain_core.messages import HumanMessage
from src.utils.formatting import format_neo4j_results
from src.utils.loaders import load_text_file

# --- CONFIGURATION ---
# (Idéalement stocké dans .env, mais on garde vos valeurs par défaut)
DEFAULT_COUNTRY = "FR"
DEFAULT_DOMAIN = "gouv.fr"
DEFAULT_ASN = 16276
URI = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH = None 

def fetch_indicator_data(indicator_path: Path, params: dict) -> str:
    """
    Parcourt le dossier, exécute tous les .cypher et retourne une grosse chaîne de texte
    contenant toutes les données structurées (comme votre ancien generate_indicator_data).
    """
    if not indicator_path.exists():
        return f"❌ Erreur : Chemin introuvable {indicator_path}"

    cypher_files = sorted(indicator_path.glob("*.cypher"))
    if not cypher_files:
        return "⚠️ Aucun fichier .cypher trouvé."

    aggregated_data = []
    print(f"📂 Lecture des données Neo4j depuis : {indicator_path.name}")

    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            
            for cypher_file in cypher_files:
                query = load_text_file(str(cypher_file))
                
                # Exécution
                records, _, _ = driver.execute_query(query, parameters_=params)
                
                # Formatage (utilise votre logique YAML/Jinja via src/utils/formatting.py)
                formatted_text = format_neo4j_results(records, str(cypher_file), params)
                aggregated_data.append(f"--- QUERY: {cypher_file.name} ---\n{formatted_text}")
                
    except Exception as e:
        return f"❌ Erreur critique BDD : {e}"

    return "\n\n".join(aggregated_data)

def save_report(content: str, indicator_path: Path, params: dict):
    """Sauvegarde le résultat final en Markdown."""
    safe_params = "_".join(f"{k}-{v}" for k, v in params.items())
    filename = f"report_{indicator_path.name}_{safe_params}.md"
    output_path = indicator_path / filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n💾 Rapport sauvegardé ici : {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Générateur de rapport Agentique (LangGraph)")
    parser.add_argument("indicator_input", help="Chemin partiel ou complet vers le dossier indicateur")
    parser.add_argument("--country", default=DEFAULT_COUNTRY)
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--asn", type=int, default=DEFAULT_ASN)
    parser.add_argument("--mode", default="smart", choices=["fast", "smart"], help="Modèle à utiliser")
    
    args = parser.parse_args()

    # 1. Résolution du chemin (votre logique originale)
    indicator_input = args.indicator_input
    base_path = Path(".")
    # Recherche simple
    found_paths = list(base_path.rglob(indicator_input))
    valid_paths = [p for p in found_paths if p.is_dir() and list(p.glob("*.cypher"))]
    
    if not valid_paths:
        print(f"❌ Indicateur introuvable : {indicator_input}")
        sys.exit(1)
    
    indicator_path = valid_paths[0] # On prend le premier trouvé
    
    params = {
        "countryCode": args.country, 
        "domainName": args.domain, 
        "hostingASN": args.asn
    }

    # 2. Récupération de la "Vérité Terrain" (Données Neo4j)
    # On le fait AVANT d'appeler l'agent pour garantir que les données brutes sont là.
    print("running queries ...")
    internal_data = fetch_indicator_data(indicator_path, params)
    print("done !")

    # 3. Construction du Prompt Utilisateur
    # On donne les données à l'agent et on lui demande de faire le travail de recherche complémentaire
    user_request = f"""
    CONTEXTE :
    Tu dois rédiger un rapport stratégique sur l'indicateur '{indicator_path.name}'.
    
    DONNÉES INTERNES (Neo4j) :
    Voici les résultats bruts de nos sondes :
    {internal_data}
    
    MISSION :
    1. Analyse ces données internes.
    2. Utilise tes outils de recherche (Google, Scraper) pour trouver le contexte "POURQUOI" (lois récentes, pannes, actualités politiques dans le pays {args.country}).
    3. Synthétise le tout en suivant strictement le format défini dans ton System Prompt.
    """

    print(f"\n🚀 Lancement de l'Agent ({args.mode})...\n")

    # 4. Appel de LangGraph
    # On passe la config pour choisir le modèle (Fast ou Smart)
    inputs = {"messages": [HumanMessage(content=user_request)]}
    config = {"configurable": {"mode": args.mode}}
    
    final_output = None
    
    # On stream pour voir les étapes (Google, Scraper, etc.)
    for event in graph.stream(inputs, config=config):
        for key, value in event.items():
            if key == "agent":
                print("🤖 [Agent] Réfléchit...")
            elif key == "tools":
                print("🛠️ [Outils] Action effectuée (Recherche/Scraping).")

    # Récupération de la réponse finale
    result = graph.invoke(inputs, config=config)
    final_response = result["messages"][-1].content

    # 5. Sauvegarde
    save_report(final_response, indicator_path, params)

if __name__ == "__main__":
    LANGCHAIN_TRACING_V2=True
    LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
    LANGCHAIN_API_KEY=os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT=os.getenv("LANGCHAIN_PROJECT")

    main()