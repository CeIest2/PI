import argparse
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import langchain
import time

# --- IMPORTS LANGCHAIN & LOCAL ---
load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "true"

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.utils.loaders import load_text_file
from src.utils.llm import get_llm
from src.tools.neo4j import fetch_indicator_data

# --- OUTILS (Utilisés directement) ---
from src.tools.google import run_deterministic_investigation

# --- CONFIGURATION ---
DEFAULT_COUNTRY = "FR"
DEFAULT_DOMAIN  = "gouv.fr"
DEFAULT_ASN     = 16276
URI             = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH            = None 

def save_report(content, indicator_path: Path, params: dict):
    """
    Saves the final report in Markdown.
    Handles both string content and structured list content (from newer LLMs).
    """
    safe_params = "_".join(f"{k}-{v}" for k, v in params.items())
    filename    = f"report_{indicator_path.name}_{safe_params}.md"
    output_path = indicator_path / filename
    
    # --- FIX: Extraction du texte si c'est une liste ---
    text_to_save = content
    
    if isinstance(content, list):
        # On concatène tous les morceaux de texte trouvés dans la liste
        # Le format semble être [{'type': 'text', 'text': '...'}, ...]
        extracted_parts = []
        for item in content:
            if isinstance(item, dict) and 'text' in item:
                extracted_parts.append(item['text'])
            elif isinstance(item, str):
                extracted_parts.append(item)
        
        text_to_save = "\n".join(extracted_parts)
    # ---------------------------------------------------

    # Sécurité supplémentaire : s'assurer que c'est bien une string à la fin
    if not isinstance(text_to_save, str):
        text_to_save = str(text_to_save)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text_to_save)
    
    print(f"\n💾 Report saved here: {output_path}")


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
    start  = time.time()
    web_context = run_deterministic_investigation(internal_data, args.country, indicator_input, mode=args.mode)
    print(f"   ⏱️  Phase 1 completed in {time.time() - start:.2f} seconds.")


    # ---------------------------------------------------------
    # PHASE 2: STRATEGIC WRITING (Reasoning Mode / Magistral)
    # ---------------------------------------------------------
    print("\n🧠 PHASE 2: Strategic Synthesis & Writing (Mode Magistral)...")
    start = time.time()
    # 1. Load Reasoning Model
    llm_writer = get_llm("report_redaction")

    # 2. Load Expert Prompt File (render_document_thinking.txt)
    current_dir = Path(__file__).parent
    prompt_file_path = os.path.join(current_dir, "prompt", "render_document_thinking.txt")


    system_prompt_content = load_text_file(str(prompt_file_path))

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
    print(final_content)  # Print first 5000 chars for preview

    # 5. Save
    save_report(final_content, indicator_path, params)
    print(f"   ⏱️  Phase 2 completed in {time.time() - start:.2f} seconds.")

if __name__ == "__main__":
    # Optional LangSmith Tracing
    LANGCHAIN_TRACING_V2=True
    LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
    LANGCHAIN_API_KEY=os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT=os.getenv("LANGCHAIN_PROJECT")
    langchain.debug = True

    main()