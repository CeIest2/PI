import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

os.environ["LANGCHAIN_TRACING_V2"] = "false" # <--- Ajoute ça tout en haut
# --- CONFIGURATION DES CHEMINS ---
# On cible le dossier parent puis request_for_YPI
current_folder = Path(__file__).parent.absolute()
target_folder = (current_folder / ".." / "request_for_YPI").resolve()

if not target_folder.exists():
    print(f"❌ ERREUR : Le dossier {target_folder} n'existe pas.")
else:
    sys.path.append(str(target_folder))
    # On se déplace dans le dossier pour que les chemins relatifs du script original (./prompt, ./src) fonctionnent
    os.chdir(target_folder)
    print(f"✅ Dossier de travail défini sur : {target_folder}")

# --- IMPORT DE TON AGENT ---
try:
    from generate_report import fetch_indicator_data, graph, get_llm
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
        # Le script s'attend à trouver un dossier "indicators" dans le dossier courant
        indicator_path = Path("indicators") / data.indicator
        
        params = {
            "countryCode": data.country, 
            "domainName": data.domain, 
            "hostingASN": data.asn
        }

        # 1. Neo4j
        internal_data = fetch_indicator_data(indicator_path, params)

        # 2. Agent LangGraph
        user_request = f"MISSION: Analyse {data.indicator} pour {data.country}. Données: {internal_data}"
        inputs = {"messages": [("human", user_request)]}
        
        # Exécution du graphe (Phase 1)
        final_state = graph.invoke(inputs, config={"configurable": {"mode": "smart"}})
        
        # 3. Rédaction Finale (Phase 2)
        llm_writer = get_llm("reasoning")
        final_response = llm_writer.invoke(final_state["messages"])

        return {"report": final_response.content}

    except Exception as e:
        print(f"🔥 Erreur lors de l'analyse : {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)