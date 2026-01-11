# src/utils/country_utils.py
import os
import re
import json
from typing import Dict, List
from pathlib import Path

def load_country_mapping() -> Dict[str, str]:
    mapping = {}
    # On remonte de src/utils vers la racine du projet pour trouver prompt/
    current_dir = Path(__file__).parent.parent.parent
    file_path = os.path.join(current_dir, "prompt", "country_code.txt")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if "->" in line:
                name, code = line.split("->")
                mapping[name.strip().lower()] = code.strip()
    return mapping

def apply_country_mapping(queries: List[str], mapping: Dict[str, str]) -> List[str]:
    processed_queries = []
    for query in queries:
        matches = re.findall(r"__COUNTRY_(.+?)__", query)
        for country_name in matches:
            code = mapping.get(country_name.lower())
            placeholder = f"__COUNTRY_{country_name}__"
            if code:
                query = query.replace(placeholder, code)
            else:
                print(f"❌ [Mapping] Pays introuvable dans le fichier : {country_name}")
        processed_queries.append(query)
    return processed_queries