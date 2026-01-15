# formating.py

def format_results_for_llm(query_path, records, query_params):
    """
    Transforme les données brutes de Neo4j en un texte lisible.
    """
    report = f"--- RAPPORT D'ANALYSE ---\n"
    report += f"Requête utilisée : {query_path}\n"
    report += f"Paramètres : {query_params}\n"
    report += f"Résultats trouvés : {len(records)}\n\n"
    
    for i, record in enumerate(records):
        report += f"Enregistrement {i+1} :\n"
        for key, value in record.items():
            report += f"  - {key}: {value}\n"
        report += "-"*20 + "\n"
    
    return report