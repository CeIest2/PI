# src/utils/formatting.py
from jinja2 import Template
from src.utils.loaders import load_yaml_file
import os

def format_neo4j_results(records, query_path: str, params: dict) -> str:
    """
    Formate les résultats bruts de Neo4j en utilisant le template YAML associé
    au dossier de la requête Cypher, comme dans votre script original.
    """
    # 1. Trouver le fichier query_templates.yaml dans le même dossier que la requête .cypher
    query_dir = os.path.dirname(query_path)
    yaml_path = os.path.join(query_dir, "query_templates.yaml")
    
    templates = load_yaml_file(yaml_path)
    
    # 2. Déterminer la clé du template (basée sur le nom du fichier cypher, ex: '1.cypher' -> '1')
    query_filename = os.path.basename(query_path)
    query_key = os.path.splitext(query_filename)[0] # "1"
    
    if query_key not in templates:
        return str([r.data() for r in records]) # Fallback brut si pas de template
        
    template_str = templates[query_key]
    
    # 3. Appliquer le template Jinja2
    # On injecte les records et les paramètres (countryCode, etc.)
    formatted_output = ""
    try:
        jinja_template = Template(template_str)
        # On suppose que le template attend une liste ou itère dessus
        # Votre logique originale semblait traiter record par record ou globalement
        formatted_output = jinja_template.render(data=records, **params)
    except Exception as e:
        formatted_output = f"Error formatting template: {e}\nRaw data: {records}"
        
    return formatted_output