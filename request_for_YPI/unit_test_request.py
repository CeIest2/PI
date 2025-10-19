from neo4j import GraphDatabase, exceptions
import logging
import os
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

# Supprimer tous les warnings
warnings.filterwarnings("ignore")

# Configuration de la connexion
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")

# Code pays à utiliser pour les tests (modifiable)
TEST_COUNTRY_CODE = "FR"

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
    
    # Parcourir tous les fichiers .cypher
    for cypher_file in base.rglob("*.cypher"):
        indicator_dir = cypher_file.parent
        
        # Vérifier qu'on est dans un dossier d'indicateur (contient un .md)
        md_files = list(indicator_dir.glob("*.md"))
        
        if md_files:
            # Utiliser le chemin relatif comme clé
            rel_path = str(indicator_dir.relative_to(base))
            
            if rel_path not in indicators:
                indicators[rel_path] = []
            
            indicators[rel_path].append(cypher_file)
    
    # Trier les fichiers dans chaque indicateur
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

def test_query(driver, query: str, query_file: str) -> Tuple[bool, str, int]:
    """
    Teste une requête Cypher.
    Retourne (succès, message, nombre_résultats)
    """
    try:
        # Remplacer le paramètre $countryCode si présent
        query_with_params = query
        params = {}
        
        if "$countryCode" in query:
            params["countryCode"] = TEST_COUNTRY_CODE
        
        # Exécuter la requête (sans récupérer les résultats détaillés)
        records, summary, keys = driver.execute_query(
            query_with_params,
            parameters_=params,
            database_="neo4j"
        )
        
        result_count = len(records)
        return True, f"OK", result_count
        
    except exceptions.CypherSyntaxError as e:
        return False, f"Erreur de syntaxe Cypher", 0
    except Exception as e:
        error_msg = str(e)[:100]  # Limiter la longueur
        return False, f"Erreur: {error_msg}", 0

def format_indicator_path(path: str) -> Tuple[str, str, str]:
    """
    Sépare le chemin en pilier / catégorie / indicateur.
    Ex: 'infrastructure/ecosysteme_fibre/portee_fibre_10km'
    -> ('infrastructure', 'ecosysteme_fibre', 'portee_fibre_10km')
    """
    parts = path.split(os.sep)
    
    pilier = parts[0] if len(parts) > 0 else ""
    categorie = parts[1] if len(parts) > 1 else ""
    indicateur = parts[2] if len(parts) > 2 else ""
    
    return pilier, categorie, indicateur

def main():
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}Test des requêtes Cypher - Yellow Pages of Internet (YPI){Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"Code pays de test: {Colors.BLUE}{TEST_COUNTRY_CODE}{Colors.RESET}\n")
    
    # Trouver tous les indicateurs et leurs fichiers
    print(f"{Colors.YELLOW}Recherche des fichiers .cypher...{Colors.RESET}")
    indicators = find_cypher_files()
    print(f"Trouvé {len(indicators)} indicateur(s)\n")
    
    # Statistiques globales
    total_queries = 0
    passed_queries = 0
    failed_queries = 0
    skipped_queries = 0
    
    # Connexion à la base de données
    print(f"{Colors.YELLOW}Connexion à Neo4j...{Colors.RESET}")
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            print(f"{Colors.GREEN}✓ Connexion réussie{Colors.RESET}\n")
            
            # Parcourir chaque indicateur
            for indicator_path in sorted(indicators.keys()):
                cypher_files = indicators[indicator_path]
                pilier, categorie, indicateur = format_indicator_path(indicator_path)
                
                # Afficher le header de l'indicateur
                print(f"{Colors.BOLD}{Colors.BLUE}{pilier}{Colors.RESET} / "
                      f"{Colors.BOLD}{categorie}{Colors.RESET} / "
                      f"{Colors.BOLD}{indicateur}{Colors.RESET}:")
                
                # Tester chaque requête (1.cypher, 2.cypher, 3.cypher)
                for i in range(1, 4):
                    expected_file = next((f for f in cypher_files if f.name == f"{i}.cypher"), None)
                    
                    if expected_file and expected_file.exists():
                        total_queries += 1
                        query_content = load_cypher_query(expected_file)
                        
                        if not query_content:
                            print(f"  cypher{i}: {Colors.YELLOW}SKIP{Colors.RESET} (fichier vide)")
                            skipped_queries += 1
                            continue
                        
                        # Tester la requête
                        success, message, count = test_query(driver, query_content, str(expected_file))
                        
                        if success:
                            print(f"  cypher{i}: {Colors.GREEN}✓ VALIDATED{Colors.RESET}")
                            passed_queries += 1
                        else:
                            print(f"  cypher{i}: {Colors.RED}✗ FAILED{Colors.RESET} - {message}")
                            failed_queries += 1
                    else:
                        print(f"  cypher{i}: {Colors.YELLOW}PASS{Colors.RESET} (fichier non trouvé)")
                        skipped_queries += 1
                
                print()  # Ligne vide entre les indicateurs
            
            # Afficher le résumé
            print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
            print(f"{Colors.BOLD}RÉSUMÉ DES TESTS{Colors.RESET}")
            print(f"{Colors.BOLD}{'='*80}{Colors.RESET}")
            print(f"Total de requêtes testées:  {total_queries}")
            print(f"{Colors.GREEN}✓ Validées:                 {passed_queries}{Colors.RESET}")
            print(f"{Colors.RED}✗ Échouées:                 {failed_queries}{Colors.RESET}")
            print(f"{Colors.YELLOW}⊘ Ignorées (vides/absentes): {skipped_queries}{Colors.RESET}")
            
            # Taux de réussite (uniquement sur les tests effectués, sans les ignorés)
            tests_executed = passed_queries + failed_queries
            if tests_executed > 0:
                success_rate = (passed_queries / tests_executed) * 100
                print(f"\n{Colors.BOLD}Taux de réussite: {success_rate:.1f}%{Colors.RESET} ({passed_queries}/{tests_executed} requêtes)")
            else:
                print(f"\n{Colors.YELLOW}Aucune requête testée{Colors.RESET}")
            
    except exceptions.ServiceUnavailable:
        print(f"{Colors.RED}✗ Erreur: Impossible de se connecter à Neo4j{Colors.RESET}")
        print(f"Vérifiez que le conteneur Docker est démarré avec: docker-compose up -d")
    except exceptions.AuthError:
        print(f"{Colors.RED}✗ Erreur d'authentification{Colors.RESET}")
        print(f"Vérifiez les identifiants dans le script")
    except Exception as e:
        print(f"{Colors.RED}✗ Erreur inattendue: {e}{Colors.RESET}")

if __name__ == "__main__":
    # Désactiver tous les warnings de Neo4j
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger("neo4j").setLevel(logging.ERROR)
    logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)
    main()