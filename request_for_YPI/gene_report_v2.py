import ast
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Charger les variables d'environnement
load_dotenv()

# Import des modules existants du dépôt
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from src.tools.google import search_google
from src.tools.scraper import read_web_page  # Import du scraper existant
from src.request_IYP.prompt_to_request import process_user_request_with_retry
from src.utils.logger import logger

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_DIR = os.path.join(BASE_DIR, "prompt", "report_generation")
SYSTEM_PROMPT_DIR = os.path.join(BASE_DIR, "prompt")

# Liste des sections à générer
REPORT_SECTIONS = [
    {"id": 1, "name": "Geopolitics", "file": "part_1_geopolitics.md"},
    {"id": 2, "name": "Infrastructure", "file": "part_2_infrastructure.md"},
    {"id": 3, "name": "Market", "file": "part_3_market.md"},
    {"id": 4, "name": "Localization", "file": "part_4_localization.md"},
    {"id": 5, "name": "Security", "file": "part_5_security.md"},
    {"id": 6, "name": "Governance", "file": "part_6_governance.md"}
]

def run_llm_step(prompt_text, mode="smart"):
    llm = get_llm(mode)
    response = llm.invoke(prompt_text)
    return response.content

def clean_llm_output(text):
    """
    Nettoie la sortie LLM.
    Gère les modèles 'Reasoning' qui renvoient une liste [Trace, ..., Réponse].
    """
    if isinstance(text, list) and len(text) > 0:
        text = text[-1]
        
    if not isinstance(text, str):
        text = str(text)

    return text.replace("```python", "").replace("```json", "").replace("```", "").strip()

def synthesize_google_findings(question, sources):
    """
    Prend une liste de contenus de pages web et rédige une synthèse factuelle.
    """
    context = ""
    for i, src in enumerate(sources, 1):
        context += f"--- SOURCE {i}: {src['title']} ({src['link']}) ---\n"
        context += f"CONTENT: {src['content'][:5000]}\n\n" # Limite pour le contexte LLM

    prompt = f"""
    You are an OSINT Expert. Based on the technical web findings below, provide a definitive and detailed answer to the question.
    Cite your sources using [Source 1], [Source 2], etc.
    
    Question: {question}
    
    Findings:
    {context}
    
    Direct Answer (Detailed & Technical):
    """
    return run_llm_step(prompt, mode="smart")

def process_single_question(q, country_name):
    """Traite une question avec scraping et synthèse automatique."""
    clean_q = q.split(']:')[-1].strip() if ']:' in q else q
    logger.info(f"🚀 Traitement : {clean_q[:50]}...")
    
    sources_list = [] # Stockera les sources pour cette question
    
    # --- CAS IYP-GRAPH ---
    if "[IYP-GRAPH]" in q:
        decomposer_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "cypher_query_decomposer.md"))
        limit_instr = "\nAll generated Cypher queries MUST strictly end with a 'LIMIT 50' clause."
        raw_intents = run_llm_step(decomposer_prompt.replace("[COUNTRY_NAME]", country_name) + limit_instr + f"\n\nInput Question: {clean_q}", mode="fast")
        technical_intents = ast.literal_eval(clean_llm_output(raw_intents))

        combined_iyp_data = []
        for intent in technical_intents:
            res = process_user_request_with_retry(intent, logger_active=True)
            combined_iyp_data.append({"intent": intent, "result": res.get("data", [])[:40]})
        
        synth_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "IYP/result_synthesizer.md"))
        final_answer = run_llm_step(synth_prompt.replace("{{INVESTIGATIVE_QUESTION}}", q).replace("{{RAW_RESULTS_DATA}}", json.dumps(combined_iyp_data)), mode="smart")
        
        # On marque la source interne
        sources_list = ["Internal Knowledge Graph (Neo4j Database)"]
        return {"question": q, "answer": final_answer, "sources": sources_list}
    

    # --- CAS GOOGLE-SEARCH ---
    elif "[GOOGLE-SEARCH]" in q:
        optimizer_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "google_query_optimizer.md"))
        optimized_queries_raw = run_llm_step(f"{optimizer_prompt}\n\nInput Question: {clean_q}", mode="fast")
        search_queries = ast.literal_eval(clean_llm_output(optimized_queries_raw))

        all_links = []
        for sq in search_queries:
            all_links.extend(search_google.run(sq, nub_site=3))

        unique_links = {l['link']: l for l in all_links if 'link' in l}.values()
        top_links = list(unique_links)[:5]

        logger.info(f"🌐 Scraping de {len(top_links)} sources pour : {clean_q[:30]}...")
        findings_with_content = []
        
        with ThreadPoolExecutor(max_workers=5) as scraper_executor:
            contents = list(scraper_executor.map(lambda l: read_web_page.run(l['link']), top_links))
            
            for link_info, content in zip(top_links, contents):
                if content and "Error" not in content[:50]:
                    findings_with_content.append({
                        "title": link_info.get('title'),
                        "link": link_info.get('link'),
                        "content": content
                    })

        if findings_with_content:
            final_answer = synthesize_google_findings(clean_q, findings_with_content)
            
            # --- AJOUT : On formate les sources pour les renvoyer ---
            for i, src in enumerate(findings_with_content, 1):
                sources_list.append(f"[Source {i}] {src['title']} ({src['link']})")
        else:
            final_answer = "No relevant web content could be retrieved."
            
        return {"question": q, "answer": final_answer, "sources": sources_list}

    return {"question": q, "answer": "Format non supporté", "sources": []}

def process_section_workflow(country_name, section):
    """Exécute le workflow complet pour UNE section (Questions -> Recherche -> Rédaction)."""
    logger.section(f"DÉMARRAGE SECTION : {section['name']}")
    
    # 1. Génération des questions
    section_strategy = load_text_file(os.path.join(PROMPT_DIR, section['file']))
    arch_template = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "question_generator_agent.md"))
    prompt_text = arch_template.replace("{{SECTION_INVESTIGATION_PROMPT}}", section_strategy).replace("[COUNTRY_NAME]", country_name)
    
    raw_questions = run_llm_step(prompt_text)
    questions = [line.strip() for line in raw_questions.split('\n') if '[' in line and ']' in line]
    logger.info(f"📋 {len(questions)} questions expertes générées. Lancement de l'investigation...")

    # 2. Exécution Parallèle (Questions)
    with ThreadPoolExecutor(max_workers=16) as executor:
        findings = list(executor.map(lambda q: process_single_question(q, country_name), questions))

    # 3. Sauvegarde dans un fichier texte propre
    filename = f"findings_{country_name}_{section['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    findings_text_block = ""  # Cette variable servira pour le rapport final

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"EXPERT FINDINGS - {section['name']} - {country_name}\n")
        f.write("="*60 + "\n\n")
        
        for item in findings:
            # Préparer les blocs de texte
            q_text = f"### QUESTION: {item['question']}\n"
            a_text = f"ANSWER:\n{item['answer']}\n"
            
            # Gérer l'affichage des sources si elles existent
            sources_text = ""
            if "sources" in item and item["sources"]:
                sources_text = "\nUSED SOURCES:\n" + "\n".join(item["sources"]) + "\n"
            
            separator = "-" * 60 + "\n\n"

            # Écrire dans le fichier texte (findings_....txt)
            full_entry = q_text + a_text + sources_text + separator
            f.write(full_entry)

            # Ajouter à la variable mémoire pour la génération du rapport
            findings_text_block += full_entry

    logger.success(f"✅ Résultats bruts sauvegardés dans : {filename}")

    # --- ÉTAPE 4 : GÉNÉRATION DU RAPPORT FINAL (MARKDOWN) ---
    final_report_markdown = generate_report_section(country_name, section['id'], findings_text_block)

    if final_report_markdown:
        # On sauvegarde la section individuelle au cas où
        report_filename = f"REPORT_{country_name}_{section['name']}_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(final_report_markdown)
        logger.success(f"📄 Section rédigée : {report_filename}")
        return final_report_markdown
    
    return None

def generate_report_section(country_name, section_id, findings_text):
    """
    Génère la section de rapport finale en Markdown à partir des résultats d'investigation.
    """
    section = next((s for s in REPORT_SECTIONS if s["id"] == section_id), None)
    if not section:
        logger.error(f"❌ Section ID {section_id} introuvable.")
        return None

    prompt_path = os.path.join(PROMPT_DIR, section['file'])
    
    if not os.path.exists(prompt_path):
        logger.error(f"❌ Fichier de prompt introuvable : {prompt_path}")
        return None

    logger.info(f"✍️  Rédaction de la section '{section['name']}' en cours...")

    section_instructions = load_text_file(prompt_path)

    writer_prompt = f"""
    You are a Lead Intelligence Analyst and Expert Technical Writer.
    
    ### MISSION
    Write the '{section['name']}' section of the Strategic Country Report for **{country_name}**.
    
    ### SECTION GUIDELINES
    {section_instructions}

    ### RAW INTELLIGENCE DATA & SOURCES
    The following text contains the research findings. 
    **CRITICAL:** This data contains specific metrics (percentages, ASN names, Hege scores, Law names).
    
    --- START OF DATA ---
    {findings_text}
    --- END OF DATA ---

    ### WRITING INSTRUCTIONS
    1. **Format**: Output strictly valid Markdown (H2, H3).
    2. **Style**: detailed, technical narrative (Intelligence Report). 
    3. **DATA PRESERVATION (IMPORTANT)**: 
       - Do NOT simplify the data. 
       - If the findings list specific percentages (e.g., "34.5%"), use the exact number. 
       - If the findings list specific entities (e.g., "AS1234 Orange"), name them.
       - Your goal is to turn the raw data into a readable text WITHOUT losing the technical depth.
    4. **Handling Missing Data**: If data is explicitly marked as "unavailable", state it clearly but briefly.
    5. **Citations**: Maintain the [Source X] links in the text.
    
    ### BIBLIOGRAPHY
    At the end, create a '## References' section listing the URLs found in 'USED SOURCES'.
    
    GENERATE THE REPORT SECTION NOW:
    """

    response = run_llm_step(writer_prompt, mode="smart")
    return clean_llm_output(response)

# --- NOUVELLE FONCTION POUR TOUT GÉNÉRER ---
def generate_full_report(country_name):
    """
    Génère le rapport complet en lançant TOUTES les sections EN PARALLÈLE.
    """
    logger.info(f"🌍 DÉMARRAGE DU RAPPORT COMPLET PARALLÈLE POUR : {country_name}")
    
    # En-tête du rapport global
    full_report_md = f"# STRATEGIC COUNTRY REPORT: {country_name.upper()}\n"
    full_report_md += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
    full_report_md += "---\n\n"

    # Dictionnaire pour stocker les résultats dans le désordre (car le parallèle finit aléatoirement)
    results = {}

    # On lance les 6 sections en même temps
    # Attention : Cela va générer beaucoup de requêtes simultanées (6 sections * 16 questions = ~96 threads potentiels)
    with ThreadPoolExecutor(max_workers=6) as executor:
        # On crée un dictionnaire {future: section_id} pour savoir qui est qui
        future_to_section = {
            executor.submit(process_section_workflow, country_name, section): section 
            for section in REPORT_SECTIONS
        }

        # On récupère les résultats au fur et à mesure qu'ils arrivent
        from concurrent.futures import as_completed
        for future in as_completed(future_to_section):
            section = future_to_section[future]
            try:
                content = future.result()
                if content:
                    results[section['id']] = content
                else:
                    results[section['id']] = f"## {section['name']}\n\n*Generation failed.*\n\n"
            except Exception as e:
                logger.error(f"🔥 Erreur critique sur la section {section['name']} : {e}")
                results[section['id']] = f"## {section['name']}\n\n*Error: {str(e)}*\n\n"

    # Assemblage final DANS L'ORDRE (1, 2, 3, 4, 5, 6)
    # On utilise REPORT_SECTIONS pour garantir l'ordre, pas l'ordre d'arrivée des threads
    for section in REPORT_SECTIONS:
        if section['id'] in results:
            full_report_md += results[section['id']] + "\n\n"
            full_report_md += "<div style='page-break-after: always;'></div>\n\n"

    # Sauvegarde
    final_filename = f"FULL_REPORT_{country_name}_{datetime.now().strftime('%Y%m%d')}.md"
    with open(final_filename, "w", encoding="utf-8") as f:
        f.write(full_report_md)
    
    logger.success(f"🏆 RAPPORT COMPLET GÉNÉRÉ (PARALLÈLE) : {final_filename}")

if __name__ == "__main__":
    # Lancement du rapport complet pour la France
    generate_full_report("France")