import ast
import os
import json
import time
import subprocess
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
            
            # --- STRUCTURE ---
            "--toc",
            "--toc-depth=2",
            "--number-sections",
            
            # --- MISE EN PAGE ---
            "--variable", "documentclass=report",
            "--variable", "geometry:a4paper,margin=2.5cm",
            "--variable", "fontsize=11pt",
            "--variable", "linestretch=1.25",
            "--variable", "parskip=10pt",
            
            # --- CORRECTION DES DÉBORDEMENTS (URL) ---
            # C'est cette ligne qui change tout : elle charge le package 'xurl'
            # qui autorise la coupe des liens n'importe où.
            "--variable", "header-includes=\\usepackage{xurl}", 
            
            # --- COULEURS ---
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
        
        # 1. Tenter l'attribut direct (Standard pour Google Vertex AI / Gemini)
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            
        # 2. Sinon chercher dans response_metadata (Standard OpenAI / Mistral)
        if not usage and hasattr(response, 'response_metadata'):
            meta = response.response_metadata
            usage = meta.get('token_usage') or meta.get('usage') or meta.get('usage_metadata')
            
        if usage:
            # Standardisation des noms de champs
            p_tokens = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
            c_tokens = usage.get("completion_tokens") or usage.get("output_tokens") or 0
            t_tokens = usage.get("total_tokens") or (p_tokens + c_tokens)
            
            TOKEN_USAGE["prompt_tokens"] += p_tokens
            TOKEN_USAGE["completion_tokens"] += c_tokens
            TOKEN_USAGE["total_tokens"] += t_tokens
            TOKEN_USAGE["calls"] += 1
        else:
            # Si toujours vide, on loggue les infos pour debug
            debug_info = list(response.response_metadata.keys()) if hasattr(response, 'response_metadata') else "Pas de metadata"
            logger.warning(f"⚠️ Stats introuvables. Clés : {debug_info}")

    except Exception as e:
        logger.warning(f"⚠️ Erreur comptage tokens : {e}")

    # Retourne le contenu
    if hasattr(response, 'content'):
        return response.content
    return str(response)



def clean_llm_output(text):
    """Nettoie la sortie LLM."""
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
    """Synthèse factuelle des résultats web."""
    context = ""
    for i, src in enumerate(sources, 1):
        content_extract = src['content'][:4000] 
        context += f"--- SOURCE {i}: {src['title']} ({src['link']}) ---\n"
        context += f"CONTENT: {content_extract}\n\n"

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


def perform_google_search_investigation(clean_q):
    """Investigation complète via Google (Optimisation -> Search -> Scraping -> Synthèse)."""
    try:
        optimizer_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "google_query_optimizer.md"))
        optimized_queries_raw = run_llm_step(f"{optimizer_prompt}\n\nInput Question: {clean_q}", mode="fast")
        
        try:
            search_queries = ast.literal_eval(clean_llm_output(optimized_queries_raw))
            if not isinstance(search_queries, list):
                search_queries = [clean_q]
        except Exception as e:
            logger.warning(f"⚠️ Erreur parsing requêtes Google ({e}), utilisation requête brute.")
            search_queries = [clean_q]

        all_links = []
        for sq in search_queries:
            try:
                all_links.extend(search_google.run(sq, nub_site=3))
            except Exception:
                continue

        unique_links = {l['link']: l for l in all_links if 'link' in l}.values()
        top_links = list(unique_links)[:5]

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

        sources_list = []
        if findings_with_content:
            final_answer = synthesize_google_findings(clean_q, findings_with_content)
            for i, src in enumerate(findings_with_content, 1):
                sources_list.append(f"[Source {i}] {src['title']} ({src['link']})")
        else:
            final_answer = "No relevant web content could be retrieved."
            
        return final_answer, sources_list

    except Exception as e:
        logger.error(f"❌ Erreur critique dans Google Investigation : {e}")
        return "Error during web investigation.", []


def process_single_question(q, country_name):
    """Traite une question avec IYP-Graph (timeout 5min) ou Google Direct."""
    clean_q = q.split(']:')[-1].strip() if ']:' in q else q
    logger.info(f"🚀 Traitement : {clean_q[:50]}...")
    
    # --- CAS 1 : RECHERCHE DIRECTE GOOGLE ---
    if "[GOOGLE-SEARCH]" in q:
        logger.info(f"🌐 Lancement recherche Google DIRECTE pour : {clean_q[:30]}")
        answer, sources = perform_google_search_investigation(clean_q)
        return {"question": q, "answer": answer, "sources": sources}

    # --- CAS 2 : IYP-GRAPH AVEC FALLBACK GOOGLE APRÈS 5 MIN ---
    elif "[IYP-GRAPH]" in q:
        def run_iyp_logic():
            try:
                decomposer_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "cypher_query_decomposer.md"))
                limit_instr       = "\nAll generated Cypher queries MUST strictly end with a 'LIMIT 50' clause."
                raw_intents       = run_llm_step(decomposer_prompt.replace("[COUNTRY_NAME]", country_name) + limit_instr + f"\n\nInput Question: {clean_q}", mode="fast")
                
                try:
                    technical_intents = ast.literal_eval(clean_llm_output(raw_intents))
                except:
                    return "Error: Failed to parse intents."

                combined_iyp_data = []
                for intent in technical_intents:
                    res = process_user_request_with_retry(intent, logger_active=True)
                    combined_iyp_data.append({"intent": intent, "result": res.get("data", [])[:40]})
                
                synth_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "IYP/result_synthesizer.md"))
                return run_llm_step(synth_prompt.replace("{{INVESTIGATIVE_QUESTION}}", q).replace("{{RAW_RESULTS_DATA}}", json.dumps(combined_iyp_data)), mode="smart")
            except Exception as e:
                return f"Internal Error in IYP Logic: {e}"

        internal_executor = ThreadPoolExecutor(max_workers=1)
        future = internal_executor.submit(run_iyp_logic)
        
        try:
            # On attend maximum 5 minutes (300s)
            final_answer = future.result(timeout=300)
            internal_executor.shutdown(wait=False)
            return {"question": q, "answer": final_answer, "sources": ["Internal Knowledge Graph (Neo4j Database)"]}
        
        except (TimeoutError, Exception) as e:
            internal_executor.shutdown(wait=False)
            
            error_type = "TIMEOUT" if isinstance(e, TimeoutError) else "ERREUR"
            logger.warning(f"⚠️ {error_type} (5min) sur IYP-GRAPH pour '{clean_q[:30]}'. Basculement immédiat sur Google Search...")
            
            answer, sources = perform_google_search_investigation(clean_q)
            fallback_msg = f"(Note: Information récupérée via Google suite à {error_type} de l'analyseur de graphe)\n\n"
            
            return {
                "question": q, 
                "answer": fallback_msg + answer, 
                "sources": sources
            }

    return {"question": q, "answer": "Format non supporté", "sources": []}

def process_section_workflow(country_name, section):
    """Exécute le workflow complet pour UNE section."""
    logger.section(f"DÉMARRAGE SECTION : {section['name']}")
    
    try:
        section_strategy = load_text_file(os.path.join(PROMPT_DIR, section['file']))
        arch_template = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "question_generator_agent.md"))
        prompt_text = arch_template.replace("{{SECTION_INVESTIGATION_PROMPT}}", section_strategy).replace("[COUNTRY_NAME]", country_name)
        
        raw_questions = run_llm_step(prompt_text)
        questions = [line.strip() for line in raw_questions.split('\n') if '[' in line and ']' in line]
        logger.info(f"📋 {len(questions)} questions expertes générées pour {section['name']}.")

        findings = []
        
        # Réduction workers à 3 pour alléger la charge
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_question = {
                executor.submit(process_single_question, q, country_name): q 
                for q in questions
            }
            
            for future in as_completed(future_to_question):
                q = future_to_question[future]
                try:
                    result = future.result(timeout=600) 
                    findings.append(result)
                except TimeoutError:
                    logger.error(f"⏰ TIMEOUT CRITIQUE process_single_question : {q[:50]}...")
                    findings.append({"question": q, "answer": "Critical Timeout.", "sources": []})
                except Exception as e:
                    logger.error(f"💥 Erreur critique thread question : {e}")
                    findings.append({"question": q, "answer": f"Error: {e}", "sources": []})

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

        logger.success(f"✅ Résultats sauvegardés : {filename}")

        final_report_markdown = generate_report_section(country_name, section['id'], findings_text_block)

        if final_report_markdown:
            report_filename = f"REPORT_{country_name}_{section['name']}_{datetime.now().strftime('%Y%m%d')}.md"
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(final_report_markdown)
            logger.success(f"📄 Section rédigée : {report_filename}")
            return final_report_markdown
        
        return None
    except Exception as e:
        logger.error(f"🔥 Erreur majeure section {section['name']} : {e}")
        return None

def generate_report_section(country_name, section_id, findings_text):
    """
    Génère la section de rapport avec un style analytique ET la préservation stricte des sources.
    """
    section = next((s for s in REPORT_SECTIONS if s["id"] == section_id), None)
    if not section:
        return None

    prompt_path = os.path.join(PROMPT_DIR, section['file'])
    section_instructions = load_text_file(prompt_path)

    # --- PROMPT CORRIGÉ (Avec Citations) ---
    writer_prompt = f"""
    You are a Senior Strategic Analyst for a National Intelligence Agency.
    You are writing a confidential report based on data extracted from the 'IYP' (Internet Yellow Pages) database.
    
    ### MISSION
    Draft the Chapter '{section['name']}' for the Country Report: **{country_name}**.
    
    ### RAW DATA (Source: IYP Database & OSINT)
    {findings_text}

    ### WRITING INSTRUCTIONS (STRICT)
    1. **NO CHAPTER TITLE**: Do NOT write '# {section['name']}'. The system adds it automatically. Start directly with the text.
    2. **MANDATORY STRUCTURE**:
       - Begin with an **"Executive Summary"** (Header: `## Executive Summary {{-}}`). 
       - Use `##` for main subsections and `###` for details.
    3. **TONE & STYLE**: 
       - **Analytical**: Explain the *strategic implication* of the data.
       - **Visual**: Use bullet points (`*`) and blockquotes (`>`) to aerate the text.
    
    4. **CITATIONS & EVIDENCE (CRITICAL)**:
       - **Preserve Sources**: You MUST keep the citation markers `[Source X]` found in the raw text.
       - **Placement**: When stating a specific fact or figure (e.g., "34% market share"), append the source immediately after (e.g., "34% market share [Source 1].").
       - **No Hallucinations**: Do not invent sources. Use only those provided in the findings.

    ### BIBLIOGRAPHY
    At the very end of your response, add a section titled:
    `## References {{-}}`
    List the URLs corresponding to the `[Source X]` tags used in your text.

    GENERATE THE CHAPTER CONTENT NOW:
    """

    response = run_llm_step(writer_prompt, mode="report_redaction")
    return clean_llm_output(response)

def generate_global_synthesis(country_name, full_report_content):
    """Génère une section de synthèse qui analyse tout le rapport précédent."""
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
    logger.info(f"🌍 DÉMARRAGE DU RAPPORT COMPLET PARALLÈLE POUR : {country_name}")
    
    # --- CORRECTION 1: MÉTADONNÉES PDF (Auteur correct + Titres propres) ---
    full_report_md = "---\n"
    full_report_md += f'title: "STRATEGIC COUNTRY REPORT: {country_name.upper()}"\n'
    full_report_md += 'subtitle: "Infrastructure, Security & Geopolitics Analysis"\n'
    # Correction du nom de l\'auteur (IYP n\'est plus l\'auteur)
    full_report_md += 'author: "Automated Strategic Analyst (v2.0)"\n' 
    full_report_md += f'date: "{datetime.now().strftime("%d %B %Y")}"\n'
    full_report_md += 'lang: "en"\n'
    full_report_md += "---\n\n"
    # --------------------------------------------------------

    results = {}
    raw_text_for_synthesis = ""

    # (Lancement parallèle inchangé...)
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

    # --- ASSEMBLAGE CORRIGÉ (Règle le problème "0.1") ---
    for section in REPORT_SECTIONS:
        if section['id'] in results:
            content = results[section['id']]
            
            # Nettoyage dictionnaire (inchangé)
            if isinstance(content, str) and content.strip().startswith("{'type':"):
                try:
                    import ast
                    parsed = ast.literal_eval(content)
                    if isinstance(parsed, dict) and 'text' in parsed:
                        content = parsed['text']
                except Exception:
                    pass

            # --- CORRECTION CRITIQUE STRUCTURE ---
            # On ajoute le TITRE DE CHAPITRE (H1) ici manuellement.
            # Cela force LaTeX à créer un "Chapitre 1", "Chapitre 2", etc.
            full_report_md += f"# {section['name']}\n\n"
            
            full_report_md += content + "\n\n"
            full_report_md += "\\newpage\n\n"
            
            raw_text_for_synthesis += content + "\n\n"

    # (Synthèse et Sauvegarde inchangées...)
    logger.info("⏳ Lancement de la génération de la synthèse finale...")
    try:
        if len(raw_text_for_synthesis) > 150000:
             raw_text_for_synthesis = raw_text_for_synthesis[:150000] + "\n\n[...TRUNCATED DATA...]"

        synthesis_content = generate_global_synthesis(country_name, raw_text_for_synthesis)
        
        # Ajout du titre de chapitre pour la synthèse aussi
        full_report_md += "# Strategic Synthesis & Roadmap\n\n"
        full_report_md += synthesis_content + "\n\n"
        
    except Exception as e:
        logger.error(f"🔥 Erreur lors de la synthèse : {e}")

    # Sauvegarde
    final_filename = f"FULL_REPORT_{country_name}_{datetime.now().strftime('%Y%m%d')}.md"
    with open(final_filename, "w", encoding="utf-8") as f:
        f.write(full_report_md)
    
    logger.success(f"🏆 RAPPORT COMPLET GÉNÉRÉ : {final_filename}")

    pdf_path = convert_to_pdf(final_filename)
    if pdf_path:
        logger.success(f"🚀 Rapport final disponible en PDF : {pdf_path}")

if __name__ == "__main__":
    start_time = time.time()
    
    try:
        generate_full_report("Tunisia")
    except Exception as e:
        logger.error(f"❌ Erreur critique : {e}")
    finally:
        # --- RAPPORT DE CONSOMMATION ---
        duration = time.time() - start_time
        logger.info("\n" + "="*40)
        logger.info("📊 BILAN DE CONSOMMATION (Est.)")
        logger.info("="*40)
        logger.info(f"⏱️  Durée totale      : {duration/60:.2f} minutes")
        logger.info(f"📞  Nombre d'appels   : {TOKEN_USAGE['calls']}")
        logger.info(f"📥  Input Tokens      : {TOKEN_USAGE['prompt_tokens']:,}")
        logger.info(f"📤  Output Tokens     : {TOKEN_USAGE['completion_tokens']:,}")
        logger.info(f"📈  TOTAL TOKENS      : {TOKEN_USAGE['total_tokens']:,}")
        
        # Estimation Coût (Basé sur prix GPT-4o standard : $2.50/1M in, $10.00/1M out)
        # Ajustez les prix selon votre modèle (Mistral, GPT-4o-mini, etc.)
        cost_in = (TOKEN_USAGE['prompt_tokens'] / 1_000_000) * 2.50
        cost_out = (TOKEN_USAGE['completion_tokens'] / 1_000_000) * 10.00
        total_cost = cost_in + cost_out
        
        logger.info(f"💰  Coût Estimé       : ${total_cost:.4f}")
        logger.info("="*40 + "\n")
        
        # Nettoyage threads
        logger.info("👋 Fin du programme.")
        os._exit(0)