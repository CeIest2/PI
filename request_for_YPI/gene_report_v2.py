import ast
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Import des modules existants de votre projet
from src.utils.llm import get_llm
from src.utils.loaders import load_text_file
from src.tools.google import search_google
from src.request_IYP.prompt_to_request import process_user_request_with_retry
from src.utils.logger import logger

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_DIR = os.path.join(BASE_DIR, "prompt", "report_generation")
SYSTEM_PROMPT_DIR = os.path.join(BASE_DIR, "prompt")

# On garde toute la liste mais on ne prendra que la première plus bas
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

def process_section_workflow(country_name, section):
    logger.section(f"SECTION DEBUG: {section['name']}")
    current_context = ""
    
    # Stratégie de la partie
    section_strategy = load_text_file(os.path.join(PROMPT_DIR, section['file']))
    
    # 1. GÉNÉRATION DES QUESTIONS PRÉCISES
    arch_template = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "question_generator_agent.md"))
    prompt_text = arch_template.replace("{{SECTION_INVESTIGATION_PROMPT}}", section_strategy).replace("[COUNTRY_NAME]", country_name)
    print(prompt_text)  # Pour debug immédiat du prompt

    raw_questions = run_llm_step(prompt_text)
    print(f"\n📝 Questions générées brutes :\n{raw_questions}\n") 

    questions = [line.strip() for line in raw_questions.split('\n') if '[' in line and ']' in line]
    logger.info(f"📋 Questions d'expert générées : {len(questions)}")

    findings = []
    for q in questions:
        clean_q = q.split(']:')[-1].strip() if ']:' in q else q
        
        if "[IYP-GRAPH]" in q:
            logger.info(f"🧠 Décomposition technique pour : {clean_q[:50]}...")
            decomposer_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "cypher_query_decomposer.md"))
            print(decomposer_prompt.replace("[COUNTRY_NAME]", country_name) + f"\n\nInput Question: {clean_q}")  # Debug prompt complet 
            raw_intents = run_llm_step(
                decomposer_prompt.replace("[COUNTRY_NAME]", country_name) + f"\n\nInput Question: {clean_q}", 
                mode="fast"
            )
            
            try:

                technical_intents = ast.literal_eval(raw_intents.strip())
            except:
                technical_intents = [clean_q] 

            logger.info(f"📡 Intentions techniques retenues : {technical_intents}")

            combined_iyp_data = []
            for intent in technical_intents:
                logger.info(f"🔍 [IYP] Exécution de l'intention : {intent}")
                res = process_user_request_with_retry(intent, logger_active=True)
                combined_iyp_data.append({"intent": intent, "result": res.get("data")})
            synth_prompt_path = os.path.join(SYSTEM_PROMPT_DIR, "IYP/result_synthesizer.md")
            synth_prompt_template = load_text_file(synth_prompt_path)

            final_text_for_this_question = run_llm_step(
                synth_prompt_template
                .replace("{{INVESTIGATIVE_QUESTION}}", q)
                .replace("{{RAW_RESULTS_DATA}}", json.dumps(combined_iyp_data)),
                mode="smart"
            )
            findings.append({"question": q, "data": final_text_for_this_question})
        
        elif "[GOOGLE-SEARCH]" in q:
            # --- NOUVELLE ÉTAPE : OPTIMISATION GOOGLE ---
            logger.info(f"🧠 Optimisation de la recherche pour : {clean_q[:50]}...")
            optimizer_prompt = load_text_file(os.path.join(SYSTEM_PROMPT_DIR, "google_query_optimizer.md"))
            
            # On génère les mots-clés
            optimized_queries_raw = run_llm_step(f"{optimizer_prompt}\n\nInput Question: {clean_q}", mode="fast")
            
            try:
                # Tentative de conversion en liste Python
                search_queries = ast.literal_eval(optimized_queries_raw.strip())
            except:
                # Fallback si le format n'est pas une liste propre
                search_queries = [clean_q]

            logger.info(f"📡 Mots-clés optimisés : {search_queries}")
            
            # On exécute les multiples recherches
            all_web_results = []
            for sq in search_queries:
                logger.info(f"🌐 Google Search en cours : {sq}")
                res = search_google.run(sq) # Utilise la fonction .run() de votre outil
                all_web_results.extend(res)
            
            findings.append({"question": q, "search_queries": search_queries, "data": all_web_results})
        print(f"\n🔎 Résultats pour la question : {clean_q}\n{json.dumps(findings[-1], indent=2)}\n")
        exit()

    # 3. CRITIQUE & RÉDACTION (simplifié pour le debug)
    logger.info("🧐 Analyse des résultats par le critique...")
    writer_prompt = f"Write the section '{section['name']}' for {country_name} based on these findings: {json.dumps(findings)}"
    content = run_llm_step(writer_prompt, mode="report_redaction")
    
    return content

def generate_single_debug_section(country_name):
    start_time = datetime.now()
    
    # ON NE PREND QUE LA PREMIÈRE SECTION (ID 1: GEOPOLITICS)
    section_to_test = REPORT_SECTIONS[0]
    
    content = process_section_workflow(country_name, section_to_test)
    
    # Affichage du résultat final dans la console pour lecture immédiate
    print("\n" + "="*50)
    print(f"RÉSULTAT FINAL POUR {section_to_test['name']}")
    print("="*50)
    print(content)
    print("="*50)
    
    logger.success(f"🏁 Test terminé en {datetime.now() - start_time}")

if __name__ == "__main__":
    generate_single_debug_section("Kazakhstan")