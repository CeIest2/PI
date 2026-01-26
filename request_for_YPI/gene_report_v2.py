import ast
import os
import json
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
    """Nettoyage des balises Markdown (```python, etc)."""
    return text.replace("```python", "").replace("```json", "").replace("```", "").strip()

def synthesize_google_findings(question, sources):
    """
    Prend une liste de contenus de pages web et rédige une synthèse factuelle.
    Inspiré par la phase de rédaction de run_deterministic_investigation.
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
        return {"question": q, "answer": final_answer}
    

    elif "[GOOGLE-SEARCH]" in q:

        optimizer_prompt      = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "google_query_optimizer.md"))
        optimized_queries_raw = run_llm_step(f"{optimizer_prompt}\n\nInput Question: {clean_q}", mode="fast")
        search_queries        = ast.literal_eval(clean_llm_output(optimized_queries_raw))

        all_links = []
        for sq in search_queries:
            all_links.extend(search_google.run(sq, nub_site=3))
        

        unique_links = {l['link']: l for l in all_links if 'link' in l}.values()
        top_links    = list(unique_links)[:5]
        

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
        else:
            final_answer = "No relevant web content could be retrieved to answer this question."
            
        return {"question": q, "answer": final_answer}

    return {"question": q, "answer": "Format non supporté"}

def process_section_workflow(country_name, section):
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
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"EXPERT FINDINGS - {section['name']} - {country_name}\n")
        f.write("="*60 + "\n\n")
        for item in findings:
            f.write(f"### QUESTION: {item['question']}\n")
            f.write(f"ANSWER:\n{item['answer']}\n")
            f.write("-" * 60 + "\n\n")

    logger.success(f"✅ Investigation terminée. Résultats compilés dans : {filename}")
    return filename

if __name__ == "__main__":
    process_section_workflow("France", REPORT_SECTIONS[0])