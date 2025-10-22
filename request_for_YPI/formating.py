import yaml
from jinja2 import Environment
from typing import List, Dict, Any
from pathlib import Path
import os

# Initialise l'environnement Jinja2 une seule fois
jinja_env = Environment(trim_blocks=True, lstrip_blocks=True)

def format_results_for_llm(
    query_path: str,
    records: List[Any],
    query_params: Dict[str, Any]
) -> str:
    """
    Formate les résultats bruts d'une requête Neo4j en utilisant un fichier
    de configuration YAML qui contient une clé principale 'queries'.
    """
    try:
        # ✅ CORRECTION : Le chemin du fichier YAML est maintenant relatif 
        # au chemin de la requête
        config_filepath = Path(query_path).parent / "query_templates.yaml"
        
        # Ce print n'est plus nécessaire mais on le garde pour vérifier
        print(f"DEBUG: Répertoire de travail actuel : {os.getcwd()}")
        print(f"DEBUG: Chemin de la requête : {query_path}")
        print(f"DEBUG: Recherche du fichier de config ici : {config_filepath.resolve()}")


        with open(config_filepath, 'r', encoding='utf-8') as f:
            all_configs = yaml.safe_load(f)
            
    except FileNotFoundError:
        # Amélioration du message d'erreur pour plus de clarté
        return f"Erreur : Le fichier de configuration '{config_filepath.resolve()}' est introuvable."
    except Exception as e:
        return f"Erreur lors de la lecture du fichier YAML '{config_filepath}': {e}"

    # ... le reste de ta fonction est correct et n'a pas besoin de changer ...

    # 1. Accéder au dictionnaire principal "queries"
    queries_dict = all_configs.get("queries")
    if not queries_dict:
        return f"Erreur : La clé de haut niveau 'queries' est introuvable dans '{config_filepath}'."
    
    # 2. La clé dans le YAML doit correspondre au NOM du fichier requête, pas au chemin complet
    # Cette approche est plus simple que celle avec le chemin complet
    query_filename = Path(query_path).name 
    query_config = queries_dict.get(query_filename)

    if not query_config or 'template' not in query_config:
        print(f"⚠️  Warning: Aucune configuration de template trouvée pour la clé '{query_filename}' dans '{config_filepath}'.")
        return f"Résultats bruts pour {query_filename}:\n{[record.data() for record in records]}"

    # Le formatage Jinja2 reste inchangé
    results_data = [record.data() for record in records]

    try:
        template = jinja_env.from_string(query_config['template'])
        formatted_output = template.render(
            results=results_data,
            params=query_params
        )
        return formatted_output.strip()
        
    except Exception as e:
        return f"Erreur lors de l'application du template pour '{query_filename}': {e}"