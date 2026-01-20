import sys
import os
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# --- CONFIGURATION DES CHEMINS ---
current_folder = Path(__file__).parent.absolute()
target_folder = (current_folder / ".." / "request_for_YPI").resolve()

if not target_folder.exists():
    print(f"❌ ERREUR : Le dossier {target_folder} n'existe pas.")
else:
    sys.path.append(str(target_folder))
    os.chdir(target_folder)
    print(f"✅ Dossier de travail défini sur : {target_folder}")

# --- IMPORT DES FONCTIONS DE TON SCRIPT ---
try:
    # On importe les outils et le getter LLM directement depuis ton script
    from generate_report import fetch_indicator_data, run_deterministic_investigation
    from src.utils.llm import get_llm
    from src.utils.loaders import load_text_file
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")
    raise

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class AnalysisInputs(BaseModel):
    indicator: str
    country: str
    domain: str
    asn: int

@app.post("/run-analysis")
async def run_analysis(data: AnalysisInputs):
    try:
        # 0. Configuration initiale
        current_date = datetime.now().strftime("%d %B %Y")
        params = {
            "countryCode": data.country, 
            "domainName": data.domain, 
            "hostingASN": data.asn
        }
        
        # 1. PHASE 1: Investigation Déterministique (Neo4j + OSINT)
        # On simule le chemin du dossier indicateur
        indicator_path = Path("indicators") / data.indicator
        
        print(f"🔍 Running Phase 1 for {data.indicator}...")
        internal_data = fetch_indicator_data(indicator_path, params)
        web_context = run_deterministic_investigation(internal_data, data.country, data.indicator, mode="smart")

        # 2. PHASE 2: Rédaction (LLM avec Reasoning)
        print("✍️ Running Phase 2: Strategic Writing...")
        llm_writer = get_llm("report_redaction")

        # Chargement du prompt expert
        prompt_file_path = target_folder / "prompt" / "render_document_thinking.txt"
        system_prompt_content = load_text_file(str(prompt_file_path))

        writer_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_content),
            MessagesPlaceholder(variable_name="history"),
            ("human", f"""
            FINAL REPORTING MISSION:
            Today is {current_date}.
            Above is the entire investigation file (Neo4j Data + Web Searches + PDF Readings).
            
            INSTRUCTIONS:
            1. Focus on the TECHNICAL FACTS and CONTEXT discovered.
            2. Write the FINAL REPORT following STRICTLY the structure requested in your System Prompt.
            3. Use your reasoning capabilities to link technical outages/data to contextual events.
            
            Output Format: Markdown.
            """)
        ])

        # Préparation du contexte pour le LLM
        investigation_summary = f"""
        1. INTERNAL NEO4J DATA (Ground Truth):
        {internal_data}
        
        2. EXTERNAL WEB FINDINGS (Controlled Search Results):
        {web_context}
        """
        
        conversation_history = [HumanMessage(content=investigation_summary)]
        
        # Exécution de la chaîne
        chain = writer_prompt | llm_writer
        final_response = chain.invoke({"history": conversation_history})

        return {"report": final_response.content}

    except Exception as e:
        print(f"🔥 Erreur lors de l'analyse : {e}")
        # On capture l'erreur complète pour le debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)