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
        path_to_md = Path("../interface_tests/report.md")
        
        if not path_to_md.exists():
            return {"report": f"❌ Fichier non trouvé : {path_to_md}"}

        with open(path_to_md, "r", encoding="utf-8") as f:
            file_content = f.read()

        # --- CORRECTION 1 : Supprimer les espaces à gauche ---
        # Le # doit être le tout premier caractère de la ligne
        header = f"# Rapport d'Analyse : {data.indicator}\n"
        header += f"**Pays cible** : {data.country} | **Domaine** : {data.domain} | **ASN** : {data.asn}\n"
        header += "---\n\n"

        # --- CORRECTION 2 : Remplacer les variables dans le corps du fichier ---
        # On remplace manuellement les placeholders {data.xxx} du fichier texte
        content_filled = file_content.replace("{data.indicator}", data.indicator)\
                                     .replace("{data.country}", data.country)\
                                     .replace("{data.asn}", str(data.asn))\
                                     .replace("{data.domain}", data.domain)

        return {"report": content_filled}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)