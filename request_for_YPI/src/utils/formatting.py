from jinja2 import Template
from src.utils.loaders import load_yaml_file
import os

def format_neo4j_results(records, query_path: str, params: dict) -> str:
    """
    Formate les résultats bruts de Neo4j en utilisant le template YAML associé.
    Gère la structure nested 'queries' -> '1.cypher' -> 'template'.
    """
    query_dir = os.path.dirname(query_path)
    yaml_path = os.path.join(query_dir, "query_templates.yaml")
    
    yaml_content = load_yaml_file(yaml_path)
    
    if not yaml_content:
        return str([r.data() for r in records])

    if "queries" in yaml_content:
        templates = yaml_content["queries"]
    else:
        templates = yaml_content

    query_filename = os.path.basename(query_path) # ex: "1.cypher"
    
    template_data = None
    if query_filename in templates:
        template_data = templates[query_filename]
    else:
        key_no_ext = os.path.splitext(query_filename)[0]
        if key_no_ext in templates:
            template_data = templates[key_no_ext]
    
    if not template_data:
        print(f"⚠️ Warning: No template key found for '{query_filename}' in {yaml_path}")
        return str([r.data() for r in records])
        

    if isinstance(template_data, dict) and "template" in template_data:
        template_str = template_data["template"]
    elif isinstance(template_data, str):
        template_str = template_data
    else:
        print(f"⚠️ Error: Template definition is invalid for '{query_filename}'")
        return str([r.data() for r in records])

    try:
        jinja_template = Template(template_str)
        formatted_output = jinja_template.render(results=[r.data() for r in records], params=params)
        return formatted_output
    except Exception as e:
        return f"Error formatting template: {e}\nRaw data: {records}"