import argparse
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from neo4j import GraphDatabase
import langchain

# --- IMPORTS LANGCHAIN & LOCAL ---
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.utils.formatting import format_neo4j_results
from src.utils.loaders import load_text_file
from src.utils.llm import get_llm
from src.tools.neo4j import fetch_indicator_data

# --- OUTILS (Utilisés directement) ---
from src.tools.google import search_google
from src.tools.scraper import read_web_page
from src.utils.index_information import get_definition
from src.utils.eval_utility import evaluate_document_relevance

# --- CONFIGURATION ---
DEFAULT_COUNTRY = "FR"
DEFAULT_DOMAIN  = "gouv.fr"
DEFAULT_ASN     = 16276
URI             = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH            = None 


def save_report(content: str, indicator_path: Path, params: dict):
    """Saves the final report in Markdown."""
    safe_params = "_".join(f"{k}-{v}" for k, v in params.items())
    filename    = f"report_{indicator_path.name}_{safe_params}.md"
    output_path = indicator_path / filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n💾 Report saved here: {output_path}")

def run_deterministic_investigation(internal_data: str, country: str, indicator_name: str, mode: str = "smart"):
    
    llm = get_llm("smart")
    
    print(f"\n🔧 [Phase 1] Génération des requêtes de recherche pour {country}...")

    search_planning_prompt = ChatPromptTemplate.from_template(load_text_file(os.path.join("prompt", "search_planning.txt")))
    chain_planner          = search_planning_prompt | llm
    resilience_index       = get_definition(indicator_name)

    response = chain_planner.invoke({
        "internal_data": internal_data[:3000], 
        "country": country,
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "resilience_index": resilience_index,
        "indicator_name": indicator_name

    })

    raw = response.content
    if isinstance(raw, list):
        content = "".join([block.get("text", "") for block in raw if isinstance(block, dict)])
    else:
        content = str(raw)

    # 2. Nettoyage du Markdown (```json ...)
    content = content.replace("```json", "").replace("```", "").strip()

    # 3. Parsing
    queries = []
    try:
        queries = json.loads(content)
        if not isinstance(queries, list):
            raise ValueError("Le résultat n'est pas une liste JSON.")
    except Exception as e:
        print(f"❌ Erreur parsing JSON: {e}")
        # Fallback de secours si le LLM a échoué
        queries = [f"{indicator_name} obstacles {country}", f"{indicator_name} strategy {country}"]

    print(f"   📋 Requêtes générées : {queries}")

    web_findings = []
    print(queries)
    for q in queries:
        print(f"   🔎 Recherche Google : {q}")
        results_links = search_google.run(q)
        
        for res in results_links:
            if isinstance(res, dict) and "error" not in res:
                title   = res.get('title', 'No Title')
                link    = res.get('link', '')
                snippet = res.get('snippet', 'No snippet')
                
                web_findings.append(f"SOURCE GOOGLE: {title}\nSNIPPET: {snippet}\nLINK: {link}")
                
                if link:
                    print(f"      📖 Lecture rapide de : {link}")
                    # read and resume page content so it not to big to fit in context
                    page_content = read_web_page.run(link)
                    if page_content:
                        # we are gonna evaluate if the document is useful for our 
                        reponse_eval = evaluate_document_relevance(summarized_text=page_content, country=country, indicator_name=indicator_name, indicator_definition=resilience_index)
                        if reponse_eval.get("decision") == "KEEP":
                            web_findings.append(f"CONTENU DÉTAILLÉ ({link}):\n{page_content[:20000]}...")
                            print(f"      ✅ Document kept for report.")
                        else:
                            print(f"      ⛔ Document discarded by relevance evaluation: {reponse_eval.get('reason','No reason provided')}")

    return "\n\n".join(web_findings)

def main():
    parser = argparse.ArgumentParser(description="Deterministic Report Generator")
    parser.add_argument("indicator_input", help="Partial or full path to the indicator folder")
    parser.add_argument("--country", default=DEFAULT_COUNTRY)
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--asn", type=int, default=DEFAULT_ASN)
    parser.add_argument("--mode", default="smart", choices=["fast", "smart"], 
                        help="Mode for RESEARCH PHASE (fast=Mistral Small, smart=Mistral Large)")
    
    args = parser.parse_args()

    # 1. Path Resolution
    indicator_input = args.indicator_input
    base_path       = Path(".")
    found_paths     = list(base_path.rglob(indicator_input))
    valid_paths     = [p for p in found_paths if p.is_dir() and list(p.glob("*.cypher"))]
    
    if not valid_paths:
        print(f"Indicator not found: {indicator_input}")
        sys.exit(1)
    
    indicator_path = valid_paths[0]
    
    params = {
        "countryCode": args.country, 
        "domainName" : args.domain, 
        "hostingASN" : args.asn
    }

    # 2. Fetch "Ground Truth" (Neo4j)
    print("running queries ...")
    internal_data = fetch_indicator_data(indicator_path, params)
    print("done !")

    # --- CURRENT DATE ---
    current_date = datetime.now().strftime("%d %B %Y")

    # ---------------------------------------------------------
    # PHASE 1: RESEARCH & INVESTIGATION (DETERMINISTIC PIPELINE)
    # ---------------------------------------------------------
    print(f"\n PHASE 1: OSINT Investigation (Mode: {args.mode})...\n")
    web_context = run_deterministic_investigation(internal_data, args.country, indicator_input, mode=args.mode)

    # ---------------------------------------------------------
    # PHASE 2: STRATEGIC WRITING (Reasoning Mode / Magistral)
    # ---------------------------------------------------------
    print("\n🧠 PHASE 2: Strategic Synthesis & Writing (Mode Magistral)...")
    
    # 1. Load Reasoning Model
    try:
        llm_writer = get_llm("reasoning")
    except Exception as e:
        print(f"⚠️ Error loading Reasoning LLM: {e}. Fallback to Smart.")
        llm_writer = get_llm("smart")
    
    # 2. Load Expert Prompt File (render_document_thinking.txt)
    current_dir = Path(__file__).parent
    prompt_file_path = os.path.join(current_dir, "prompt", "render_document_thinking.txt")
    
    system_prompt_content = ""
    try:
        print(f"📄 Loading Expert Prompt from: {prompt_file_path}")
        system_prompt_content = load_text_file(str(prompt_file_path))
    except Exception as e:
        print(f"⚠️ Critical Error: Could not read prompt file ({e}).")
        system_prompt_content = "You are an expert analyst. Write a comprehensive report based on the history."

    # 3. Create Writing Prompt (ENGLISH)
    writer_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_content), # Your Expert File injected here
        MessagesPlaceholder(variable_name="history"), # Reçoit notre contexte synthétique
        ("human", f"""
        FINAL REPORTING MISSION:
        
        Today is {current_date}.
        Above is the entire investigation file (Neo4j Data + Web Searches + PDF Readings).
        
        INSTRUCTIONS:
        1. Focus on the TECHNICAL FACTS and CONTEXT discovered.
        2. Write the FINAL REPORT following STRICTLY the structure requested in your System Prompt.
        3. Use your reasoning capabilities to link technical outages/data to contextual events (laws, weather, politics).
        4. The final output must be in the language requested by the System Prompt (usually French or English), but your reasoning should be grounded in these facts.
        
        Output Format: Markdown.
        """)
    ])
    
    # Préparation du "contexte" qui remplace l'historique de conversation de l'agent
    investigation_summary = f"""
    1. INTERNAL NEO4J DATA (Ground Truth):
    {internal_data}
    
    2. EXTERNAL WEB FINDINGS (Controlled Search Results):
    {web_context}
    """
    
    # On simule un historique de conversation pour satisfaire le template
    conversation_history = [HumanMessage(content=investigation_summary)]
    
    # 4. Generate Final Report
    print("   ↳ ✍️  Writing in progress (Reasoning model may take time)...")
    chain = writer_prompt | llm_writer
    
    final_response_msg = chain.invoke({"history": conversation_history})
    final_content = final_response_msg.content

    # 5. Save
    save_report(final_content, indicator_path, params)

if __name__ == "__main__":
    # Optional LangSmith Tracing
    LANGCHAIN_TRACING_V2=True
    LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
    LANGCHAIN_API_KEY=os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT=os.getenv("LANGCHAIN_PROJECT")
    langchain.debug = True

    main()