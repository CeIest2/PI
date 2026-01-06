import argparse
import sys
import os
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
from src.agents.graph import graph
from src.utils.formatting import format_neo4j_results
from src.utils.loaders import load_text_file
from src.utils.llm import get_llm 

# --- CONFIGURATION ---
DEFAULT_COUNTRY = "FR"
DEFAULT_DOMAIN  = "gouv.fr"
DEFAULT_ASN     = 16276
URI             = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH            = None 

def fetch_indicator_data(indicator_path: Path, params: dict) -> str:

    if not indicator_path.exists(): return f"   Error: Path not found {indicator_path}"

    cypher_files = sorted(indicator_path.glob("*.cypher"))
    
    if not cypher_files: return "No .cypher files found."

    aggregated_data = []
    print(f"Reading Neo4j data from: {indicator_path.name}")

    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            
            for cypher_file in cypher_files:
                query = load_text_file(str(cypher_file))
                
                # Execution
                records, _, _ = driver.execute_query(query, parameters_=params)
                
                # Formatting
                formatted_text = format_neo4j_results(records, str(cypher_file), params)
                aggregated_data.append(f"--- QUERY: {cypher_file.name} ---\n{formatted_text}")
                
    except Exception as e:
        return f"Critical DB Error: {e}"

    return "\n\n".join(aggregated_data)

def save_report(content: str, indicator_path: Path, params: dict):
    """Saves the final report in Markdown."""
    safe_params = "_".join(f"{k}-{v}" for k, v in params.items())
    filename    = f"report_{indicator_path.name}_{safe_params}.md"
    output_path = indicator_path / filename
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n💾 Report saved here: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Agentic Report Generator (Hybrid Architecture)")
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

    # 3. Investigation Prompt (ENGLISH)
    # Goal: Gather facts, do not write the report yet.
    user_request = f"""
    ROLE: Senior Internet Infrastructure Analyst (Investigation Phase).
    CURRENT REAL WORLD DATE: {current_date}
    
    OBJECTIVE: Gather confirmed information for '{indicator_path.name}'.
    TARGET: Country {args.country}, Domain {args.domain}, ASN {args.asn}.
    
    1. INTERNAL DATA (Ground Truth):
    {internal_data}
    
    2. OSINT GUIDELINES (STRICT):
    - The Google Search tool accesses the REAL INTERNET. 
    - DO NOT search for events in the future relative to {current_date}.
    - DO NOT invent or guess URLs. Only scrape URLs explicitly returned by the 'search_google' tool.
    - If Google returns 0 results, broaden your query (remove 'site:' filters or specific years).
    
    MISSION:
    - Search for LATEST available reports
    - Find general laws and regulations currently in effect.
    - Identify technical infrastructure details using the provided information.
    """

    # ---------------------------------------------------------
    # PHASE 1: RESEARCH & INVESTIGATION (User selected mode)
    # ---------------------------------------------------------
    print(f"\n PHASE 1: OSINT Investigation (Mode: {args.mode})...\n")
    
    inputs = {"messages": [HumanMessage(content=user_request)]}
    config = {"configurable": {"mode": args.mode}} 
    
    # Stream execution to see progress
    for event in graph.stream(inputs, config=config):
        for key, value in event.items():
            if key == "agent":
                print("🤖 [Agent] Analysing...")
            elif key == "tools":
                print("🛠️ [Tools] Data fetched.")

    # Retrieve full history
    final_state = graph.invoke(inputs, config=config)
    conversation_history = final_state["messages"]
    
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
    prompt_file_path = current_dir / "prompt" / "render_document_thinking.txt"
    
    system_prompt_content = ""
    try:
        print(f"📄 Loading Expert Prompt from: {prompt_file_path.name}")
        system_prompt_content = load_text_file(str(prompt_file_path))
    except Exception as e:
        print(f"⚠️ Critical Error: Could not read prompt file ({e}).")
        system_prompt_content = "You are an expert analyst. Write a comprehensive report based on the history."

    # 3. Create Writing Prompt (ENGLISH)
    writer_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_content), # Your Expert File injected here
        MessagesPlaceholder(variable_name="history"),
        ("human", f"""
        FINAL REPORTING MISSION:
        
        Today is {current_date}.
        Above is the entire investigation file (Neo4j Data + Web Searches + PDF Readings).
        
        INSTRUCTIONS:
        1. Ignore trivial conversation messages ("I am searching...", "Here is the result").
        2. Focus on the TECHNICAL FACTS and CONTEXT discovered.
        3. Write the FINAL REPORT following STRICTLY the structure requested in your System Prompt.
        4. Use your reasoning capabilities to link technical outages/data to contextual events (laws, weather, politics).
        5. The final output must be in the language requested by the System Prompt (usually French or English), but your reasoning should be grounded in these facts.
        
        Output Format: Markdown.
        """)
    ])
    
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