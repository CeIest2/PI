import ast
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
# CORRECTION : Ajout de as_completed et TimeoutError pour gérer les blocages
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

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
    """
    Nettoie la sortie LLM.
    Gère les modèles 'Reasoning', les Dictionnaires, et les chaînes représentant des dictionnaires.
    """
    import ast

    if isinstance(text, list) and len(text) > 0:
        text = text[-1]
    
    if isinstance(text, dict):
        return str(text.get('text', text)).strip()

    if isinstance(text, str):
        text = text.strip()

        if text.startswith("{") and "'type':" in text and "'text':" in text:
            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, dict) and 'text' in parsed:
                    return str(parsed['text']).strip()
            except Exception:
                pass

    if not isinstance(text, str):
        text = str(text)

    return text.replace("```python", "").replace("```json", "").replace("```", "").strip()

def synthesize_google_findings(question, sources):
    """
    Prend une liste de contenus de pages web et rédige une synthèse factuelle.
    """
    context = ""
    for i, src in enumerate(sources, 1):
        # CORRECTION : Limite stricte par source pour éviter l'erreur "Token Limit Exceeded"
        content_extract = src['content'][:4000] 
        context += f"--- SOURCE {i}: {src['title']} ({src['link']}) ---\n"
        context += f"CONTENT: {content_extract}\n\n"

    # CORRECTION : Limite globale du contexte (ex: 100k chars max)
    if len(context) > 100000:
        context = context[:100000] + "\n...[TRUNCATED DUE TO LENGTH]..."

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
    
    sources_list = [] 

    if "[IYP-GRAPH]" in q:
        decomposer_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "cypher_query_decomposer.md"))
        limit_instr = "\nAll generated Cypher queries MUST strictly end with a 'LIMIT 50' clause."
        raw_intents = run_llm_step(decomposer_prompt.replace("[COUNTRY_NAME]", country_name) + limit_instr + f"\n\nInput Question: {clean_q}", mode="fast")
        technical_intents = ast.literal_eval(clean_llm_output(raw_intents))

        combined_iyp_data = []
        for intent in technical_intents:
            # Note : Assurez-vous que process_user_request_with_retry gère aussi ses propres timeouts
            res = process_user_request_with_retry(intent, logger_active=True)
            combined_iyp_data.append({"intent": intent, "result": res.get("data", [])[:40]})
        
        synth_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "IYP/result_synthesizer.md"))
        final_answer = run_llm_step(synth_prompt.replace("{{INVESTIGATIVE_QUESTION}}", q).replace("{{RAW_RESULTS_DATA}}", json.dumps(combined_iyp_data)), mode="smart")
        
        sources_list = ["Internal Knowledge Graph (Neo4j Database)"]
        return {"question": q, "answer": final_answer, "sources": sources_list}
    

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
            
            for i, src in enumerate(findings_with_content, 1):
                sources_list.append(f"[Source {i}] {src['title']} ({src['link']})")
        else:
            final_answer = "No relevant web content could be retrieved."
            
        return {"question": q, "answer": final_answer, "sources": sources_list}

    return {"question": q, "answer": "Format non supporté", "sources": []}

def process_section_workflow(country_name, section):
    """Exécute le workflow complet pour UNE section (Questions -> Recherche -> Rédaction)."""
    logger.section(f"DÉMARRAGE SECTION : {section['name']}")
    
    section_strategy = load_text_file(os.path.join(PROMPT_DIR, section['file']))
    arch_template = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "question_generator_agent.md"))
    prompt_text = arch_template.replace("{{SECTION_INVESTIGATION_PROMPT}}", section_strategy).replace("[COUNTRY_NAME]", country_name)
    
    raw_questions = run_llm_step(prompt_text)
    questions = [line.strip() for line in raw_questions.split('\n') if '[' in line and ']' in line]
    logger.info(f"📋 {len(questions)} questions expertes générées. Lancement de l'investigation...")

    findings = []
    
    # CORRECTION : Réduction drastique des workers (16 -> 5) pour éviter les deadlocks
    # Utilisation de as_completed pour gérer les timeouts par question
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_question = {
            executor.submit(process_single_question, q, country_name): q 
            for q in questions
        }
        
        for future in as_completed(future_to_question):
            q = future_to_question[future]
            try:
                # CORRECTION : Timeout de 300s (5min) par question. Si ça bloque, on tue la tâche.
                result = future.result(timeout=300)
                findings.append(result)
            except TimeoutError:
                logger.error(f"⏰ TIMEOUT sur la question : {q[:50]}... (Abandon)")
                findings.append({
                    "question": q, 
                    "answer": "Error: Investigation timed out (took > 5mins).", 
                    "sources": []
                })
            except Exception as e:
                logger.error(f"💥 Erreur critique sur {q[:50]}... : {e}")
                findings.append({
                    "question": q, 
                    "answer": f"Error during processing: {str(e)}", 
                    "sources": []
                })

    filename = f"findings_{country_name}_{section['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    findings_text_block = ""  

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"EXPERT FINDINGS - {section['name']} - {country_name}\n")
        f.write("="*60 + "\n\n")
        
        for item in findings:
            q_text = f"### QUESTION: {item['question']}\n"
            a_text = f"ANSWER:\n{item['answer']}\n"
            
            sources_text = ""
            if "sources" in item and item["sources"]:
                sources_text = "\nUSED SOURCES:\n" + "\n".join(item["sources"]) + "\n"
            
            separator = "-" * 60 + "\n\n"

            full_entry = q_text + a_text + sources_text + separator
            f.write(full_entry)
            findings_text_block += full_entry

    logger.success(f"✅ Résultats bruts sauvegardés dans : {filename}")

    # --- ÉTAPE 4 : GÉNÉRATION DU RAPPORT FINAL (MARKDOWN) ---
    final_report_markdown = generate_report_section(country_name, section['id'], findings_text_block)

    if final_report_markdown:
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

    response = run_llm_step(writer_prompt, mode="report_redaction")
    return clean_llm_output(response)

def generate_global_synthesis(country_name, full_report_content):
    """
    Génère une section de synthèse qui analyse tout le rapport précédent.
    """
    logger.info(f"🧠 DÉMARRAGE DE L'ANALYSE STRATÉGIQUE (Synthèse) pour : {country_name}")
    
    prompt_path = os.path.join(PROMPT_DIR, "part_7_synthesis.md")
    
    if not os.path.exists(prompt_path):
        logger.error(f"❌ Prompt de synthèse introuvable : {prompt_path}")
        return "## Strategic Synthesis\n\n*Error: Prompt missing.*"

    synthesis_template = load_text_file(prompt_path)
    
    prompt = f"""
    {synthesis_template.replace("[COUNTRY_NAME]", country_name)}

    ### FULL REPORT CONTEXT
    Below is the complete technical report generated so far. Use this content to identify problems and build the roadmap.
    If some sections contain errors, ignore them and base your strategy on available data.
    
    --- BEGIN REPORT ---
    {full_report_content}
    --- END REPORT ---
    
    GENERATE THE SYNTHESIS AND ROADMAP NOW (In Markdown):
    """
    
    response = run_llm_step(prompt, mode="report_redaction")
    return clean_llm_output(response)

def generate_full_report(country_name):
    """
    Génère le rapport complet en lançant TOUTES les sections EN PARALLÈLE,
    PUIS lance la synthèse en séquentiel.
    
    Inclut un nettoyage de secours pour les sorties mal formatées ({'type':...}).
    """
    logger.info(f"🌍 DÉMARRAGE DU RAPPORT COMPLET PARALLÈLE POUR : {country_name}")
    
    full_report_md = f"# STRATEGIC COUNTRY REPORT: {country_name.upper()}\n"
    full_report_md += f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
    full_report_md += "---\n\n"

    results = {}
    raw_text_for_synthesis = "" # Stockage pour le contexte de l'IA

    # Lancement parallèle
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_section = {
            executor.submit(process_section_workflow, country_name, section): section 
            for section in REPORT_SECTIONS
        }

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

    # Assemblage dans l'ordre + NETTOYAGE D'URGENCE
    for section in REPORT_SECTIONS:
        if section['id'] in results:
            content = results[section['id']]
            
            # --- EMERGENCY CLEANUP: Si le texte est un dictionnaire stringifié ---
            if isinstance(content, str) and content.strip().startswith("{'type':"):
                try:
                    import ast
                    parsed = ast.literal_eval(content)
                    if isinstance(parsed, dict) and 'text' in parsed:
                        logger.warning(f"⚠️ Nettoyage automatique du format dictionnaire détecté dans {section['name']}")
                        content = parsed['text'] # On récupère le vrai texte
                except Exception as parse_error:
                    logger.warning(f"⚠️ Échec du nettoyage dictionnaire pour {section['name']}: {parse_error}")
            # -------------------------------------------------------------------

            full_report_md += content + "\n\n"
            full_report_md += "<div style='page-break-after: always;'></div>\n\n"
            
            # On accumule pour la synthèse
            raw_text_for_synthesis += content + "\n\n"

    # Génération de la synthèse (Part 7)
    logger.info("⏳ Lancement de la génération de la synthèse finale...")
    try:
        # SÉCURITÉ : Tronquer le contexte si trop long (ex: > 150k caractères)
        # Cela évite l'erreur "Token Limit Exceeded" sur la synthèse
        if len(raw_text_for_synthesis) > 150000:
             logger.warning("⚠️ Contexte de synthèse trop long, troncature à 150k caractères.")
             raw_text_for_synthesis = raw_text_for_synthesis[:150000] + "\n\n[...TRUNCATED DATA...]"

        synthesis_content = generate_global_synthesis(country_name, raw_text_for_synthesis)
        
        full_report_md += "# PART 7: STRATEGIC SYNTHESIS & ROADMAP\n\n"
        full_report_md += synthesis_content + "\n\n"
        
    except Exception as e:
        logger.error(f"🔥 Erreur lors de la synthèse : {e}")
        full_report_md += "\n\n## Synthesis Error\nCould not generate recommendations."

    # Sauvegarde
    final_filename = f"FULL_REPORT_{country_name}_{datetime.now().strftime('%Y%m%d')}.md"
    with open(final_filename, "w", encoding="utf-8") as f:
        f.write(full_report_md)
    
    logger.success(f"🏆 RAPPORT COMPLET AVEC SYNTHÈSE GÉNÉRÉ : {final_filename}")

if __name__ == "__main__":
    # CORRECTION : On appelle juste la fonction principale qui gère tout
    generate_full_report("France")