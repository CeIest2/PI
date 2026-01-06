# src/utils/loaders.py
import os
import yaml

def load_text_file(path: str) -> str:
    """Lit un fichier texte brut (ex: prompt, .cypher)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_yaml_file(path: str) -> dict:
    """Lit un fichier de configuration YAML."""
    if not os.path.exists(path):
        # Si le template n'existe pas, on renvoie un dict vide pour éviter le crash
        print(f"⚠️ Warning: YAML template not found at {path}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)