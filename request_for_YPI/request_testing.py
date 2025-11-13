import sys
import argparse
from neo4j import GraphDatabase, exceptions

# ==========================================================
#  CONFIGURATION DE LA CONNEXION NEO4J
# ==========================================================
# Modifiez ces valeurs pour correspondre à votre configuration
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
    """
    Charge une requête Cypher depuis un fichier spécifié.
    En cas d'erreur (fichier non trouvé, etc.), le script s'arrête.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            print(f"✅ Fichier '{file_path}' lu avec succès.")
            return f.read()
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier '{file_path}' n'a pas été trouvé.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue lors de la lecture du fichier : {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """
    Fonction principale du script.
    """
    parser = argparse.ArgumentParser(
        description="Exécute une requête Cypher d'un fichier sur une base Neo4j."
    )
    parser.add_argument(
        "file_path", 
        help="Le chemin vers le fichier .cypher contenant la requête."
    )
    
    # --- MODIFICATION ICI : Ajout du paramètre 'default' ---
    parser.add_argument(
        "--country", 
        default=DEFAULT_COUNTRY,
        help=f"Valeur pour le paramètre $countryCode (défaut: {DEFAULT_COUNTRY})"
    )
    parser.add_argument(
        "--domain", 
        default=DEFAULT_DOMAIN,
        help=f"Valeur pour le paramètre $domainName (défaut: {DEFAULT_DOMAIN})"
    )
    parser.add_argument(
        "--asn", 
        type=int, 
        default=DEFAULT_ASN,
        help=f"Valeur pour le paramètre $hostingASN (défaut: {DEFAULT_ASN})"
    )

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
            print("✔️ Connexion réussie !")

            print("\n🚀 Exécution de la requête...")
            records, summary, _ = driver.execute_query(
                cypher_query,
                parameters_=params,
                database_="neo4j"
            )

            print("\n" + "="*30)
            print(f"📊 RÉSULTATS ({len(records)} enregistrements)")
            print("="*30)

            if not records:
                print("La requête n'a retourné aucun résultat.")
            else:
                for i, record in enumerate(records):
                    print(f"--- Enregistrement #{i + 1} ---")
                    for key, value in record.data().items():
                        print(f"  - {key}: {value}")
                print("##################")
                print(records)

            print("\n" + "="*30)
            print("📝 RÉSUMÉ DE L'EXÉCUTION")
            print("="*30)
            print(f"Requête exécutée en : {summary.result_available_after} ms")
            print(f"Base de données ciblée : '{summary.database}'")

    except exceptions.ServiceUnavailable:
        print(f"\n❌ Erreur : Impossible de se connecter à Neo4j sur {URI}.", file=sys.stderr)
        sys.exit(1)
    except exceptions.AuthError:
        print("\n❌ Erreur : Authentification refusée. Vérifiez vos identifiants.", file=sys.stderr)
        sys.exit(1)
    except exceptions.CypherSyntaxError as e:
        print(f"\n❌ Erreur de syntaxe Cypher : {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Une erreur inattendue est survenue : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()