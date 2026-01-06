import sys
import argparse
from neo4j import GraphDatabase, exceptions

from formating import format_results_for_llm 

# ==========================================================
#  CONFIGURATION DE LA CONNEXION NEO4J
# ==========================================================
# LOCAL TEST SERVER
#URI = "bolt://localhost:7687"
#AUTH = ("neo4j", "password")

# SERVER TEST CANADA
URI = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH = None
# ==========================================================

# ==========================================================
#  PARAMÈTRES PAR DÉFAUT POUR LES REQUÊTES
# ==========================================================
DEFAULT_COUNTRY = "FR"
DEFAULT_DOMAIN = "gouv.fr"
DEFAULT_ASN = 16276
# ==========================================================

def load_query_from_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{file_path}' n'a pas été trouvé.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue lors de la lecture du fichier : {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Exécute une requête Cypher et formate le résultat pour un LLM."
    )
    parser.add_argument("file_path", help="Le chemin vers le fichier .cypher contenant la requête.")
    parser.add_argument("--country", default=DEFAULT_COUNTRY, help=f"Code pays (défaut: {DEFAULT_COUNTRY})")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help=f"Nom de domaine (défaut: {DEFAULT_DOMAIN})")
    parser.add_argument("--asn", type=int, default=DEFAULT_ASN, help=f"Numéro d'AS (défaut: {DEFAULT_ASN})")
    args = parser.parse_args()

    cypher_query = load_query_from_file(args.file_path)
    
    params = {
        "countryCode": args.country,
        "domainName": args.domain,
        "hostingASN": args.asn
    }

    print(f"⚙️  Paramètres utilisés : {params}")

    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            print("⚡️ Connexion à la base de données Neo4j...")
            driver.verify_connectivity()
            
            print("🚀 Exécution de la requête...")
            records, summary, _ = driver.execute_query(
                cypher_query,
                parameters_=params,
                database_="neo4j"
            )

            print("\n" + "="*50)
            print("✅ RÉSULTAT BRUT REÇU DE NEO4J")
            print("="*50)
            print(f"{len(records)} enregistrement(s) trouvé(s).")

            print("\n" + "="*50)
            print("✨ RÉSULTAT FORMATÉ POUR LE LLM (via query_templates.yaml)")
            print("="*50)
            

            formatted_text = format_results_for_llm(
                query_path=args.file_path,
                records=records,
                query_params=params
            )
    
            print(formatted_text)



    except exceptions.ServiceUnavailable:
        print(f"\n❌ Erreur : Impossible de se connecter à Neo4j sur {URI}.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()