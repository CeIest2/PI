import ast
import os
import json
import time
import re
import subprocess
import multiprocessing
from datetime import datetime
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# Charger les variables d'environnement
load_dotenv()

# Import des modules existants du dépôt
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from src.tools.google import search_google
from src.tools.scraper import read_web_page
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

TOKEN_USAGE = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "calls": 0
}

# --- FONCTIONS UTILITAIRES ---

def clean_markdown_content(text):
    """
    Nettoie les artefacts de l'IA avant l'assemblage du rapport.
    """
    if not text: return ""

    text = re.sub(r'(?i)^(?:Table of Contents|Contents|Sommaire).*?(?=\n##|\n#)', '', text, flags=re.DOTALL)
    text = re.sub(r'^"\d+.*?",".*?"\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\d\.]+\s+(##+)', r'\1', text, flags=re.MULTILINE)
    text = re.sub(r'^#\s+(.*)', r'## \1', text, flags=re.MULTILINE)

    return text.strip()

def convert_to_pdf(md_filepath):
    """
    Convertit le fichier Markdown en PDF via LaTeX avec gestion des URL longues.
    """
    pdf_filepath = md_filepath.replace(".md", ".pdf")
    logger.info(f"⏳ Conversion en PDF Design lancée : {pdf_filepath}")
    
    try:
        cmd = [
            "pandoc", md_filepath, 
            "-o", pdf_filepath, 
            "--from", "markdown+yaml_metadata_block",
            "--standalone",
            "--pdf-engine=xelatex",
            "--toc", "--toc-depth=2", "--number-sections",
            "--variable", "documentclass=report",
            "--variable", "geometry:a4paper,margin=2.5cm",
            "--variable", "fontsize=11pt",
            "--variable", "linestretch=1.25",
            "--variable", "parskip=10pt",
            "--variable", "header-includes=\\usepackage{xurl}", 
            "--variable", "colorlinks=true",
            "--variable", "linkcolor=blue",
            "--variable", "urlcolor=blue",
            "--variable", "toccolor=black",
        ]

        subprocess.run(cmd, check=True)
        logger.success(f"✅ PDF Professionnel (URLs corrigées) : {pdf_filepath}")
        return pdf_filepath
    except FileNotFoundError:
        logger.error("❌ Pandoc n'est pas installé.")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur Pandoc : {e}")
    return None

def run_llm_step(prompt_text, mode="smart"):
    global TOKEN_USAGE
    llm = get_llm(mode)
    response = llm.invoke(prompt_text)
    
    try:
        usage = None
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
        if not usage and hasattr(response, 'response_metadata'):
            meta = response.response_metadata
            usage = meta.get('token_usage') or meta.get('usage') or meta.get('usage_metadata')
            
        if usage:
            p_tokens = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
            c_tokens = usage.get("completion_tokens") or usage.get("output_tokens") or 0
            t_tokens = usage.get("total_tokens") or (p_tokens + c_tokens)
            TOKEN_USAGE["prompt_tokens"] += p_tokens
            TOKEN_USAGE["completion_tokens"] += c_tokens
            TOKEN_USAGE["total_tokens"] += t_tokens
            TOKEN_USAGE["calls"] += 1
    except Exception as e:
        logger.warning(f"⚠️ Erreur comptage tokens : {e}")

    if hasattr(response, 'content'):
        return response.content
    return str(response)

def clean_llm_output(text):
    import ast
    if isinstance(text, list) and len(text) > 0: text = text[-1]
    if isinstance(text, dict): return str(text.get('text', text)).strip()
    if isinstance(text, str):
        text = text.strip()
        if text.startswith("{") and "'type':" in text and "'text':" in text:
            try:
                parsed = ast.literal_eval(text)
                if isinstance(parsed, dict) and 'text' in parsed:
                    return str(parsed['text']).strip()
            except Exception: pass
    if not isinstance(text, str): text = str(text)
    return text.replace("```python", "").replace("```json", "").replace("```", "").strip()

def synthesize_google_findings(question, sources):
    context = ""
    for i, src in enumerate(sources, 1):
        content_extract = src['content'][:4000] 
        context += f"--- SOURCE {i}: {src['title']} ({src['link']}) ---\nCONTENT: {content_extract}\n\n"
    if len(context) > 100000: context = context[:100000] + "\n...[TRUNCATED]..."

    prompt = f"""
    You are an OSINT Expert. Based on the technical web findings below, provide a definitive answer.
    Cite sources [Source X].
    Question: {question}
    Findings: {context}
    Direct Answer:
    """
    return run_llm_step(prompt, mode="smart")

def perform_google_search_investigation(clean_q):
    try:
        optimizer_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "google_query_optimizer.md"))
        optimized_queries_raw = run_llm_step(f"{optimizer_prompt}\n\nInput Question: {clean_q}", mode="fast")
        try:
            search_queries = ast.literal_eval(clean_llm_output(optimized_queries_raw))
            if not isinstance(search_queries, list): search_queries = [clean_q]
        except: search_queries = [clean_q]

        all_links = []
        for sq in search_queries:
            try: all_links.extend(search_google.run(sq, nub_site=3))
            except: continue

        unique_links = {l['link']: l for l in all_links if 'link' in l}.values()
        top_links = list(unique_links)[:5]
        findings_with_content = []
        
        with ThreadPoolExecutor(max_workers=5) as scraper_executor:
            contents = list(scraper_executor.map(lambda l: read_web_page.run(l['link']), top_links))
            for link_info, content in zip(top_links, contents):
                if content and "Error" not in content[:50]:
                    findings_with_content.append({"title": link_info.get('title'), "link": link_info.get('link'), "content": content})

        sources_list = []
        if findings_with_content:
            final_answer = synthesize_google_findings(clean_q, findings_with_content)
            for i, src in enumerate(findings_with_content, 1):
                sources_list.append(f"[Source {i}] {src['title']} ({src['link']})")
        else:
            final_answer = "No relevant web content could be retrieved."
            
        return final_answer, sources_list
    except Exception as e:
        logger.error(f"❌ Google Error: {e}")
        return "Error during web investigation.", []

# --- LOGIQUE IYP DANS UN PROCESSUS ISOLÉ ---

def _worker_iyp_logic(q, country_name, system_prompt_dir, return_dict):
    try:
        clean_q = q.split(']:')[-1].strip() if ']:' in q else q
        
        decomposer_prompt = load_text_file(os.path.join(system_prompt_dir, "cypher_query_decomposer.md"))
        limit_instr = "\nAll generated Cypher queries MUST strictly end with a 'LIMIT 50' clause."
        
        raw_intents = run_llm_step(decomposer_prompt.replace("[COUNTRY_NAME]", country_name) + limit_instr + f"\n\nInput Question: {clean_q}", mode="fast")
        
        try:
            technical_intents = ast.literal_eval(clean_llm_output(raw_intents))
            if not isinstance(technical_intents, list): technical_intents = [raw_intents]
        except:
            return_dict['error'] = "Failed to parse intents"
            return

        combined_iyp_data = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_intent = {
                executor.submit(process_user_request_with_retry, intent, logger_active=True): intent 
                for intent in technical_intents
            }
            for future in as_completed(future_to_intent):
                try:
                    res = future.result()
                    combined_iyp_data.append({"intent": future_to_intent[future], "result": res.get("data", [])[:40]})
                except Exception: pass

        if not combined_iyp_data:
            return_dict['result'] = "No data found via Graph."
            return

        synth_prompt = load_text_file(os.path.join(system_prompt_dir, "IYP/result_synthesizer.md"))
        final_answer = run_llm_step(synth_prompt.replace("{{INVESTIGATIVE_QUESTION}}", q).replace("{{RAW_RESULTS_DATA}}", json.dumps(combined_iyp_data)), mode="smart")
        
        return_dict['result'] = final_answer

    except Exception as e:
        return_dict['error'] = str(e)


def process_single_question(q, country_name):
    clean_q = q.split(']:')[-1].strip() if ']:' in q else q
    logger.info(f"🚀 Traitement Question : {clean_q[:50]}...")
    
    if "[GOOGLE-SEARCH]" in q:
        logger.info(f"🌐 Lancement recherche Google DIRECTE pour : {clean_q[:30]}")
        answer, sources = perform_google_search_investigation(clean_q)
        return {"question": q, "answer": answer, "sources": sources}

    elif "[IYP-GRAPH]" in q:
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        
        p = multiprocessing.Process(
            target=_worker_iyp_logic,
            args=(q, country_name, SYSTEM_PROMPT_DIR, return_dict)
        )
        p.start()
        p.join(timeout=480)
        
        if p.is_alive():
            logger.warning(f"🔪 KILL PROCESS (Timeout 8min) pour : {clean_q[:30]}...")
            p.terminate()
            p.join()
            logger.info("🌐 Basculement Google immédiat post-kill...")
            answer, sources = perform_google_search_investigation(clean_q)
            return {"question": q, "answer": f"(Timeout Graph) {answer}", "sources": sources}
        
        if 'error' in return_dict:
            return {"question": q, "answer": f"Error: {return_dict['error']}", "sources": []}
            
        return {"question": q, "answer": return_dict.get('result', "No Data"), "sources": ["Internal Graph"]}

    return {"question": q, "answer": "Format non supporté", "sources": []}


def process_section_workflow(country_name, section, previous_context=""):
    """Exécute le workflow pour UNE section avec conscience du contexte précédent (MÉMOIRE TOTALE)."""
    logger.section(f"DÉMARRAGE SECTION : {section['name']}")
    
    try:
        # 1. Génération des questions
        section_strategy = load_text_file(os.path.join(PROMPT_DIR, section['file']))
        arch_template = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "question_generator_agent.md"))
        
        # --- LOGIQUE MÉMOIRE TOTALE ---
        context_instruction = ""
        if previous_context:
            # On tronque pour éviter de saturer le context window si le rapport devient énorme
            safe_context = previous_context[-50000:] if len(previous_context) > 50000 else previous_context
            
            context_instruction = f"""
            ### 🧠 CONTEXTUAL MEMORY (READ CAREFULLY)
            The following report chapters have ALREADY been written by your colleagues.
            
            --- BEGIN PREVIOUS CHAPTERS ---
            {safe_context}
            --- END PREVIOUS CHAPTERS ---
            
            ### ⚡ YOUR MISSION
            1. **READ** the text above.
            2. **IDENTIFY GAPS**: What is missing? What logic was started but not finished?
            3. **AVOID REPETITION**: Do NOT ask questions that are already answered in the text above.
            4. **DIG DEEPER**: Based on the findings above, ask the "Second Order" questions. 
            """
        
        prompt_text = arch_template.replace("{{SECTION_INVESTIGATION_PROMPT}}", section_strategy + context_instruction).replace("[COUNTRY_NAME]", country_name)
        
        raw_questions_response = run_llm_step(prompt_text)
        
        raw_questions = clean_llm_output(raw_questions_response)
        
        questions = [line.strip() for line in raw_questions.split('\n') if '[' in line and ']' in line]
        logger.info(f"📋 {len(questions)} questions expertes générées pour {section['name']}.")

        # 2. Investigation
        findings = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_question = {
                executor.submit(process_single_question, q, country_name): q 
                for q in questions
            }
            for future in as_completed(future_to_question):
                q = future_to_question[future]
                try:
                    result = future.result(timeout=600)
                    findings.append(result)
                except Exception as e:
                    logger.error(f"💥 Erreur thread question : {e}")
                    findings.append({"question": q, "answer": f"Error: {e}", "sources": []})

        # Sauvegarde intermédiaire
        filename = f"findings_{country_name}_{section['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        findings_text_block = ""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"EXPERT FINDINGS - {section['name']} - {country_name}\n")
            for item in findings:
                entry = f"### Q: {item['question']}\nANSWER: {item['answer']}\nSOURCE: {item.get('sources', [])}\n\n"
                f.write(entry)
                findings_text_block += entry

        # 3. Rédaction
        # Note: Pour la rédaction, on garde aussi le contexte pour l'anti-redondance, mais sous forme d'instruction
        final_report_markdown = generate_report_section(country_name, section['id'], findings_text_block, previous_context)
        
        # SAUVEGARDE UNITAIRE (OPTIONNELLE MAIS UTILE)
        if final_report_markdown:
            section_filename = f"CHAPTER_{section['id']}_{section['name']}_{country_name}.md"
            with open(section_filename, "w", encoding="utf-8") as f:
                f.write(final_report_markdown)
            logger.info(f"💾 Chapitre sauvegardé individuellement : {section_filename}")

        return final_report_markdown
        
    except Exception as e:
        logger.error(f"🔥 Erreur majeure section {section['name']} : {e}")
        return None

def generate_report_section(country_name, section_id, findings_text, previous_context=""):
    section = next((s for s in REPORT_SECTIONS if s["id"] == section_id), None)
    if not section: return None
    
    # --- 1. GESTION DE LA MÉMOIRE (ANTI-DOUBLON) ---
    context_block = ""
    if previous_context:
        safe_context = previous_context[-30000:] if len(previous_context) > 30000 else previous_context
        # Notez les doubles accolades {{ }} ici aussi pour éviter les erreurs si safe_context en contient
        context_block = f"""
        ### 🧠 CONTEXTUAL MEMORY (PREVIOUS CHAPTERS)
        The following text contains chapters ALREADY generated.
        **YOUR MANDATE:**
        1. READ this context.
        2. NO REPETITION: Do not re-explain concepts already covered.
        3. LINKING: You can refer back to previous chapters.
        
        --- BEGIN PREVIOUS CONTEXT ---
        {safe_context}
        --- END PREVIOUS CONTEXT ---
        """
    else:
        context_block = "No previous chapters written yet."

    # --- 2. LE PROMPT RÉDACTEUR (CORRIGÉ) ---
    # J'ai doublé les accolades autour de {-} pour que Python les ignore
    writer_prompt = f"""
    You are a Senior Strategic Analyst for a National Intelligence Agency.
    Draft the Chapter '{section['name']}' for the Country Report: **{country_name}**.
    
    ### 🛑 CRITICAL FORMATTING RULES (FAILURE TO COMPLY = REJECTED):
    1. **NO NUMBERING**: Do NOT write "1.1" or "Chapter 1". Just "## Title".
    2. **NO TOC**: Start directly with the Executive Summary.
    3. **CITATIONS**: Every specific fact must have a citation `[Source X]` or `[IYP-GRAPH]`.
    4. **MANDATORY BIBLIOGRAPHY**: You **MUST** end the chapter with a specific section listing the sources used. Look at the "RAW INTELLIGENCE" block to find the URLs and Titles corresponding to [Source X].
    5. **CLEAN MARKDOWN**: No CSVs, no artifacts.

    {context_block}

    ### 🆕 RAW INTELLIGENCE (Contains Source Details & URLs)
    **Use the data below to write the chapter AND the bibliography:**
    {findings_text}

    ### REQUIRED STRUCTURE
    ## Executive Summary {{-}} 
    (Narrative summary with citations)

    ## [Subtopic 1]
    (Analysis...)
    
    ## [Subtopic 2]
    (Analysis...)

    ## References {{-}}
    * [Source 1] Title of the article (https://full-url-found-in-findings...)
    * [Source 2] Title...
    * [IYP-GRAPH] Internal Knowledge Graph (Neo4j)

    GENERATE THE CHAPTER CONTENT NOW:
    """

    response = run_llm_step(writer_prompt, mode="report_redaction")
    clean_response = clean_llm_output(response)
    return clean_markdown_content(clean_response)

def generate_global_synthesis(country_name, full_report_content):
    logger.info(f"🧠 DÉMARRAGE DE L'ANALYSE STRATÉGIQUE (Synthèse) pour : {country_name}")
    prompt_path = os.path.join(PROMPT_DIR, "part_7_synthesis.md")
    synthesis_template = load_text_file(prompt_path)
    
    prompt = f"""
    {synthesis_template.replace("[COUNTRY_NAME]", country_name)}

    ### FULL REPORT CONTEXT
    Below is the complete technical report generated so far.
    --- BEGIN REPORT ---
    {full_report_content}
    --- END REPORT ---
    
    GENERATE THE SYNTHESIS AND ROADMAP NOW (In Markdown):
    """
    response = run_llm_step(prompt, mode="report_redaction")
    return clean_llm_output(response)

def generate_full_report(country_name):
    logger.info(f"🌍 DÉMARRAGE DU RAPPORT SÉQUENTIEL POUR : {country_name}")
    
    # En-tête du fichier Markdown final
    full_report_md = "---\n"
    full_report_md += f'title: "STRATEGIC COUNTRY REPORT: {country_name.upper()}"\n'
    full_report_md += 'author: "Automated Strategic Analyst (v2.1)"\n' 
    full_report_md += f'date: "{datetime.now().strftime("%d %B %Y")}"\n'
    full_report_md += "---\n\n"

    raw_text_for_synthesis = ""
    completed_sections_list = [] 

    for section in REPORT_SECTIONS:
        logger.info(f"🔄 Traitement Séquentiel : {section['name']}...")
        
        current_context = raw_text_for_synthesis
        
        content = process_section_workflow(country_name, section, previous_context=current_context)
        
        if content and len(content) > 50: 
            full_report_md += f"# {section['name']}\n\n"
            full_report_md += content + "\n\n\\newpage\n\n"
            
            raw_text_for_synthesis += f"\n\n--- PREVIOUS CHAPTER: {section['name']} ---\n{content}"
            
            completed_sections_list.append(section['name'])
            logger.success(f"✅ Section '{section['name']}' terminée et ajoutée à la mémoire.")
        else:
            logger.error(f"❌ Echec ou contenu vide sur {section['name']}")

    # --- GÉNÉRATION DE LA SYNTHÈSE FINALE ---
    logger.info("⏳ Génération de la synthèse finale...")
    try:
        # On tronque si le rapport est gigantesque (> 150k caractères) pour éviter de casser l'API
        if len(raw_text_for_synthesis) > 150000:
             raw_text_for_synthesis = raw_text_for_synthesis[:150000] + "\n[TRUNCATED]"

        synthesis_content = generate_global_synthesis(country_name, raw_text_for_synthesis)
        full_report_md += "# Strategic Synthesis & Roadmap\n\n" + synthesis_content + "\n\n"
        
    except Exception as e:
        logger.error(f"🔥 Erreur synthèse : {e}")

    # --- SAUVEGARDE ET CONVERSION ---
    final_filename = f"FULL_REPORT_{country_name}_{datetime.now().strftime('%Y%m%d')}.md"
    with open(final_filename, "w", encoding="utf-8") as f:
        f.write(full_report_md)
    
    logger.success(f"🏆 RAPPORT TERMINÉ : {final_filename}")
    convert_to_pdf(final_filename)




if __name__ == "__main__":
    start_time = time.time()
    try:
        generate_full_report("France")
    except Exception as e:
        logger.error(f"❌ Erreur critique : {e}")
    finally:
        duration = time.time() - start_time
        logger.info("\n" + "="*40)
        logger.info(f"📊 Durée totale : {duration/60:.2f} minutes")
        logger.info(f"💰 Coût Estimé  : ${(TOKEN_USAGE['prompt_tokens']*2.5 + TOKEN_USAGE['completion_tokens']*10)/1000000:.4f}")
        logger.info("="*40 + "\n")
        os._exit(0)