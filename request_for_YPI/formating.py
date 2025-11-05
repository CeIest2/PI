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
    Formate the brut results of a query using a Jinja2 template defined in a YAML configuration file.
    """
    try:
        config_filepath = Path(query_path).parent / "query_templates.yaml"
        
        print(f"DEBUG: Répertoire de travail actuel : {os.getcwd()}")
        print(f"DEBUG: Chemin de la requête : {query_path}")
        print(f"DEBUG: Recherche du fichier de config ici : {config_filepath.resolve()}")


        with open(config_filepath, 'r', encoding='utf-8') as f:
            all_configs = yaml.safe_load(f)
            
    except FileNotFoundError:
        return f"Erreur : Le fichier de configuration '{config_filepath.resolve()}' est introuvable."
    except Exception as e:
        return f"Erreur lors de la lecture du fichier YAML '{config_filepath}': {e}"


    queries_dict = all_configs.get("queries")
    if not queries_dict:
        return f"Erreur : La clé de haut niveau 'queries' est introuvable dans '{config_filepath}'."

    query_filename = Path(query_path).name 
    query_config   = queries_dict.get(query_filename)

    if not query_config or 'template' not in query_config:
        print(f"⚠️  Warning: No config template has been found : '{query_filename}' in '{config_filepath}'.")
        return f"Result for {query_filename}:\n{[record.data() for record in records]}"

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