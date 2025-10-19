from neo4j import GraphDatabase, exceptions
import logging
import os
import warnings
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Supprimer tous les warnings
warnings.filterwarnings("ignore")

# Configuration de la connexion
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")

# ==========================================================
#  PARAMÈTRES DE TEST DE BASE
# ==========================================================
# MODIFIÉ : Ajout des arguments de test de base ici
TEST_COUNTRY_CODE = "FR"
TEST_DOMAIN_NAME = "gouv.fr"
TEST_HOSTING_ASN = 16276
# ==========================================================


# Couleurs pour l'affichage terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def find_cypher_files(base_path: str = ".") -> Dict[str, List[Path]]:
    """
    Parcourt l'arborescence et regroupe les fichiers .cypher par indicateur.
    Retourne un dictionnaire: {chemin_indicateur: [fichiers_cypher]}
    """
    base = Path(base_path)
    indicators = {}
    for cypher_file in base.rglob("*.cypher"):
        indicator_dir = cypher_file.parent
        if list(indicator_dir.glob("*.md")):
            rel_path = str(indicator_dir.relative_to(base))
            if rel_path not in indicators:
                indicators[rel_path] = []
            indicators[rel_path].append(cypher_file)
    for key in indicators:
        indicators[key] = sorted(indicators[key], key=lambda x: x.name)
    return indicators

def load_cypher_query(file_path: Path) -> str:
    """Charge le contenu d'un fichier .cypher"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return content if content else None
    except Exception as e:
        logging.error(f"Erreur lors de la lecture de {file_path}: {e}")
        return None

# MODIFIÉ : La fonction est mise à jour pour gérer tous les paramètres de base
def test_query(driver, query: str, query_file: str) -> Tuple[bool, str, int, float]:
    """
    Teste une requête Cypher.
    Retourne (succès, message, nombre_résultats, temps_execution)
    """
    try:
        params = {}
        
        # Vérifie chaque paramètre possible et l'ajoute s'il est présent dans la requête
        if "$countryCode" in query:
            params["countryCode"] = TEST_COUNTRY_CODE
        if "$domainName" in query:
            params["domainName"] = TEST_DOMAIN_NAME
        if "$hostingASN" in query:
            params["hostingASN"] = TEST_HOSTING_ASN

        start_time = time.time()
        
        records, summary, keys = driver.execute_query(
            query, # On passe la requête originale
            parameters_=params,
            database_="neo4j"
        )
        
        elapsed_time = time.time() - start_time
        result_count = len(records)
        
        return True, "OK", result_count, elapsed_time
        
    except exceptions.CypherSyntaxError as e:
        return False, "Erreur de syntaxe Cypher", 0, 0.0
    except Exception as e:
        error_msg = str(e)[:150]
        return False, f"Erreur: {error_msg}", 0, 0.0

def format_indicator_path(path: str) -> Tuple[str, str, str]:
    """Sépare le chemin en pilier / catégorie / indicateur."""
    parts = path.split(os.sep)
    pilier = parts[0] if parts else ""
    categorie = parts[1] if len(parts) > 1 else ""
    indicateur = parts[2] if len(parts) > 2 else ""
    return pilier, categorie, indicateur

def main():
    print(f"{Colors.BOLD}{'='*80}\nTest des requêtes Cypher - YPI\n{'='*80}{Colors.RESET}")
    print(f"Paramètres de test: country='{TEST_COUNTRY_CODE}', domain='{TEST_DOMAIN_NAME}', asn={TEST_HOSTING_ASN}\n")
    
    indicators = find_cypher_files()
    print(f"Trouvé {len(indicators)} indicateur(s) avec des requêtes.\n")
    
    total_queries, passed_queries, failed_queries, skipped_queries = 0, 0, 0, 0
    
    print(f"{Colors.YELLOW}Connexion à Neo4j...{Colors.RESET}")
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            print(f"{Colors.GREEN}✓ Connexion réussie{Colors.RESET}\n")
            
            for indicator_path in sorted(indicators.keys()):
                cypher_files = indicators[indicator_path]
                pilier, categorie, indicateur = format_indicator_path(indicator_path)
                
                print(f"{Colors.BOLD}{Colors.BLUE}{pilier}{Colors.RESET} / {Colors.BOLD}{categorie}{Colors.RESET} / {Colors.BOLD}{indicateur}{Colors.RESET}:")
                
                # Boucle pour tester 1.cypher, 2.cypher, etc.
                for i in range(1, 4):
                    expected_file = next((f for f in cypher_files if f.name == f"{i}.cypher"), None)
                    
                    if expected_file and expected_file.exists():
                        total_queries += 1
                        query_content = load_cypher_query(expected_file)
                        
                        if not query_content:
                            print(f"  cypher{i}: {Colors.YELLOW}SKIP{Colors.RESET} (fichier vide)")
                            skipped_queries += 1
                            continue
                        
                        success, message, count, exec_time = test_query(driver, query_content, str(expected_file))
                        
                        if success:
                            time_str = f"{exec_time*1000:.0f}ms" if exec_time < 1 else f"{exec_time:.2f}s"
                            print(f"  cypher{i}: {Colors.GREEN}✓ VALIDATED{Colors.RESET} ({count} résultats en {time_str})")
                            passed_queries += 1
                        else:
                            print(f"  cypher{i}: {Colors.RED}✗ FAILED{Colors.RESET} - {message}")
                            failed_queries += 1
                    else:
                        # Moins verbeux: n'affiche rien si le fichier n'existe pas.
                        pass
                
                print()

            # Afficher le résumé
            print(f"{Colors.BOLD}{'='*80}\n{Colors.BOLD}RÉSUMÉ DES TESTS\n{'='*80}{Colors.RESET}")
            print(f"Total de requêtes testées:  {total_queries}")
            print(f"{Colors.GREEN}✓ Validées:                 {passed_queries}{Colors.RESET}")
            print(f"{Colors.RED}✗ Échouées:                 {failed_queries}{Colors.RESET}")
            print(f"{Colors.YELLOW}⊘ Ignorées (vides):         {skipped_queries}{Colors.RESET}")
            
            tests_executed = passed_queries + failed_queries
            if tests_executed > 0:
                success_rate = (passed_queries / tests_executed) * 100
                print(f"\n{Colors.BOLD}Taux de réussite: {success_rate:.1f}%{Colors.RESET} ({passed_queries}/{tests_executed} requêtes)")
            else:
                print(f"\n{Colors.YELLOW}Aucune requête testée{Colors.RESET}")
            
    except exceptions.ServiceUnavailable:
        print(f"{Colors.RED}✗ Erreur: Impossible de se connecter à Neo4j{Colors.RESET}")
    except exceptions.AuthError:
        print(f"{Colors.RED}✗ Erreur d'authentification{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}✗ Erreur inattendue: {e}{Colors.RESET}")

if __name__ == "__main__":
    logging.getLogger("neo4j").setLevel(logging.ERROR)
    main()