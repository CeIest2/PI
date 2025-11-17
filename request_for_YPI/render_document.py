# render_document.py

import sys
import argparse
import os
from pathlib import Path
from neo4j import GraphDatabase, exceptions
from typing import Dict, Any, List

# Nouveaux imports pour la version récente de la bibliothèque Mistral
from mistralai import Mistral

# Import de votre module de formatage
from formating import format_results_for_llm

# ==========================================================
#  CONFIGURATION & CONSTANTS
# ==========================================================

# LOCAL TEST SERVER
#URI = "bolt://localhost:7687"
#AUTH = ("neo4j", "password")

# SERVER TEST CANADA
URI = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH = None


DEFAULT_COUNTRY = "FR"
DEFAULT_DOMAIN = "gouv.fr"
DEFAULT_ASN = 16276
# ==========================================================

def generate_LLM_respond(text_input: str) -> str:
    """
    Sending a request to Mistral LLM to generate a report based on the provided text input.
    """
    print("\nConnexion to Mistral LLM...")
    try:

        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            with open("api_key_mistral", "r", encoding="utf-8") as f:
                api_key = f.read().strip()
        
        if not api_key:
            raise ValueError("Clé API Mistral introuvable. Définissez MISTRAL_API_KEY ou créez le fichier 'api_key_mistral'.")

        client = Mistral(api_key=api_key)
        model  = "mistral-large-2411" 

        
        system_prompt = """
        Tu es un expert en analyse de l'écosystème Internet.
        Tu reçois des données brutes structurées provenant de requêtes sur une base de données.
        Ta mission est de synthétiser ces informations en un rapport clair, concis et bien structuré au format Markdown.
        Commence directement par le rapport sans phrases d'introduction comme "Voici le rapport".
        Utilise des titres, des listes à puces et du gras pour améliorer la lisibilité.
        Ton but à la fin du rapport est de fournir des conseil et des actions qui pourraient être mise en place par des policy maker pour améliorer la situation vis-à-vis de l'indice de résilience étudié.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_input}
        ]

        # Appel à l'API avec la nouvelle méthode standard
        chat_response = client.chat.complete(
                model=model,
                messages=messages,
            )

        return chat_response.choices[0].message.content

    except FileNotFoundError:
        return "❌ Erreur : Fichier 'api_key_mistral' introuvable et variable d'environnement MISTRAL_API_KEY non définie."
    except Exception as e:
        return f"❌ Une erreur est survenue lors de l'appel à l'API Mistral : {e}"


def generate_indicator_data(
    indicator_path: str, 
    query_params: Dict[str, Any],
    driver: GraphDatabase.driver
) -> str:
    """
    Finds all .cypher files for an indicator, executes them, formats the results,
    and returns a single aggregated string for an LLM.
    """
    base_path = Path(indicator_path)
    if not base_path.is_dir():
        print(f"❌ Erreur : Le répertoire de l'indicateur '{indicator_path}' est introuvable.", file=sys.stderr)
        return ""

    cypher_files = sorted(base_path.glob("*.cypher"))
    
    if not cypher_files:
        print(f"🟡 Avertissement : Aucun fichier .cypher trouvé dans '{indicator_path}'.", file=sys.stderr)
        return ""

    all_formatted_results: List[str] = []

    for query_file in cypher_files:
        try:
            with open(query_file, 'r', encoding='utf-8') as f:
                cypher_query = f.read()
            if not cypher_query.strip():
                print("     (fichier ignoré car vide)")
                continue
                
            records, _, _ = driver.execute_query(
                cypher_query, parameters_=query_params, database_="neo4j"
            )
            formatted_text = format_results_for_llm(
                query_path=str(query_file), records=records, query_params=query_params
            )
            all_formatted_results.append(formatted_text)

        except Exception as e:
            error_message = f"Erreur lors du traitement de {query_file.name}: {e}"
            print(f"     ❌ {error_message}", file=sys.stderr)
            all_formatted_results.append(f"--- ERREUR POUR {query_file.name} ---\n{error_message}")

    print("\n✅ Toutes les requêtes ont été traitées.")
    return "\n\n---\n\n".join(all_formatted_results)


def main():
    parser = argparse.ArgumentParser(description="Génère un rapport de données pour un indicateur via Neo4j et Mistral.")
    # MODIFICATION 1: L'argument s'appelle 'indicator_input' et accepte un nom ou un chemin
    parser.add_argument("indicator_input", help="Nom du dossier de l'indicateur (ex: manrs_score) ou chemin relatif (ex: security/routing_hygiene/manrs_score).")
    parser.add_argument("--country", default=DEFAULT_COUNTRY, help=f"Code pays (défaut: {DEFAULT_COUNTRY})")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help=f"Nom de domaine (défaut: {DEFAULT_DOMAIN})")
    parser.add_argument("--asn", type=int, default=DEFAULT_ASN, help=f"Numéro d'AS (défaut: {DEFAULT_ASN})")
    args = parser.parse_args()

    # MODIFICATION 2: Logique pour trouver le chemin complet de l'indicateur
    indicator_input = args.indicator_input
    indicator_path = ""

    # Cas 1: L'utilisateur a donné un chemin relatif qui existe
    potential_path = Path(indicator_input)
    if potential_path.is_dir() and list(potential_path.glob("*.cypher")) and list(potential_path.glob("*.md")):
        indicator_path = str(potential_path)
    else:
        # Cas 2: L'utilisateur n'a donné que le nom final (ex: 'manrs_score')
        # On recherche ce nom récursivement depuis le répertoire courant
        base_search_path = Path(".") 
        found_paths = []
        
        # Utilise rglob pour trouver tous les dossiers correspondants
        for path in base_search_path.rglob(indicator_input):
            # Vérifie si c'est un dossier ET que le nom correspond exactement
            if path.is_dir() and path.name == indicator_input:
                # Vérifie si c'est un dossier d'indicateur valide (contient .cypher et .md)
                if list(path.glob("*.cypher")) and list(path.glob("*.md")):
                    found_paths.append(path)

        if not found_paths:
            print(f"❌ Erreur : Aucun répertoire d'indicateur nommé '{indicator_input}' (contenant .cypher/.md) trouvé.", file=sys.stderr)
            sys.exit(1)
        
        if len(found_paths) > 1:
            print(f"❌ Erreur : Nom d'indicateur '{indicator_input}' ambigu. Plusieurs correspondances trouvées :", file=sys.stderr)
            for p in found_paths:
                print(f"   - {p}", file=sys.stderr)
            print("Veuillez spécifier un chemin plus précis (ex: security/routing_hygiene/manrs_score).", file=sys.stderr)
            sys.exit(1)
            
        indicator_path = str(found_paths[0])
    
    # FIN DE LA MODIFICATION 2

    params = {"countryCode": args.country, "domainName": args.domain, "hostingASN": args.asn}
    
    # Le reste du script utilise 'indicator_path' qui est maintenant le chemin complet résolu
    print("="*60 + f"\n🚀 DÉBUT - Indicateur : {indicator_path}\n" + "="*60)

    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            print("⚡️ Connexion à Neo4j... ✔️")
            driver.verify_connectivity()

            final_llm_input = generate_indicator_data(indicator_path, params, driver)

            print("\n\n" + "="*60 + "\n📦 DONNÉES CONSOLIDÉES (POUR LE LLM)\n" + "="*60)
            print(final_llm_input)

            # Si des données ont été générées, on appelle le LLM
            if final_llm_input and final_llm_input.strip():
                llm_report = generate_LLM_respond(final_llm_input)
                print("\n\n" + "="*60 + "\n📄 RAPPORT FINAL GÉNÉRÉ PAR LE LLM\n" + "="*60)
                print(llm_report)
                save_document(llm_report, indicator_path, params)
            else:
                print("\n🟡 Aucune donnée n'a été générée, le LLM ne sera pas appelé.")
            
    except exceptions.ServiceUnavailable:
        print(f"\n❌ Erreur : Impossible de se connecter à Neo4j sur {URI}.", file=sys.stderr)
        sys.exit(1)
    except exceptions.AuthError:
        print("\n❌ Erreur d'authentification Neo4j. Vérifiez vos identifiants.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Une erreur inattendue est survenue : {e}", file=sys.stderr)
        sys.exit(1)


def save_document(content: str, indicator_path: str, params: Dict[str, Any]) -> None:
    """
    Sauvegarde le rapport généré dans un fichier Markdown.
    Le nom du fichier inclut l'indicateur et les paramètres utilisés.
    """
    base_path       = Path(indicator_path)
    safe_params     = "_".join(f"{key}-{value}" for key, value in params.items())
    # Utilise le nom du dossier de l'indicateur pour le rapport
    output_filename = f"report_{base_path.name}_{safe_params}.md"
    output_path     = base_path / output_filename

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n💾 Rapport sauvegardé dans : {output_path.resolve()}")
    except Exception as e:
        print(f"\n❌ Erreur lors de la sauvegarde du rapport : {e}", file=sys.stderr)

if __name__ == "__main__":
    main()