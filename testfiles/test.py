import os
import requests
from dotenv import load_dotenv

# Charge les variables du fichier .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
cx_id = os.getenv("GOOGLE_CX_ID")

print(f"--- DIAGNOSTIC ---")
print(f"Clé API chargée : {'OUI' if api_key else 'NON'}")
print(f"CX ID chargé : {'OUI' if cx_id else 'NON'}")
print(f"Valeur CX ID (premiers char) : {cx_id[:5] if cx_id else 'None'}")
print("------------------")

if not api_key or not cx_id:
    print("ERREUR : Il manque la clé API ou le CX ID dans le .env")
    exit()

# On tente une requête manuelle vers Google
url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": api_key,
    "cx": cx_id,
    "q": "test python"  # Une recherche bidon pour tester
}

try:
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code == 200:
        print("✅ SUCCÈS ! La connexion fonctionne.")
    else:
        print(f"❌ ERREUR GOOGLE ({response.status_code}) :")
        # C'est ici qu'on verra le vrai message
        print(data) 
except Exception as e:
    print(f"Erreur script : {e}")