from dotenv import load_dotenv
from src.request_IYP.prompt_to_request import process_user_request_with_retry
from src.utils.logger import logger
import json

def pretty_print_result(result: dict):
    """Affiche le résultat de manière formatée."""
    print("\n" + "="*80)
    print("📊 RÉSULTAT FINAL")
    print("="*80)
    
    status = result.get("status", "UNKNOWN")
    
    if status == "SUCCESS":
        print(f"✅ Statut: {status}")
        print(f"🔄 Tentatives: {result.get('attempts', 'N/A')}")
        print(f"\n📝 Requête finale:")
        print(f"   {result.get('final_query', 'N/A')[:200]}...")
        print(f"\n📦 Données ({len(result.get('data', []))} résultats):")
        for i, item in enumerate(result.get('data', [])[:3], 1):
            print(f"   [{i}] {json.dumps(item, indent=6, ensure_ascii=False)}")
        if len(result.get('data', [])) > 3:
            print(f"   ... et {len(result.get('data', [])) - 3} autres résultats")
    
    elif status == "FAILED":
        print(f"❌ Statut: {status}")
        print(f"🔄 Tentatives: {result.get('attempts', 'N/A')}")
        print(f"🔬 Cycles de recherche: {result.get('research_cycles', 0)}")
        print(f"\n📋 Raison: {result.get('reason', 'N/A')}")
        print(f"\n📜 Historique ({len(result.get('history', []))} entrées):")
        for h in result.get('history', [])[-3:]:
            print(f"   - Tentative {h.get('attempt')}: {h.get('count', 0)} lignes")
    
    elif status == "IMPOSSIBLE":
        print(f"🚫 Statut: {status}")
        print(f"💬 Message: {result.get('message', 'N/A')}")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    load_dotenv()
    
    # Test avec la requête YouTube
    logger.section("Test Pipeline avec Requête Complexe")
    
    request = """
Dans combien de pays l'infrastructure de réseau de Facebook est-elle présente ?
    """
    
    logger.info(f"📝 Requête utilisateur: {request.strip()}")
    
    # Exécution
    result = process_user_request_with_retry(request)
    
    # Affichage du résultat
    pretty_print_result(result)
    
    # Tests supplémentaires (optionnels)
    print("\n" + "🧪 TESTS SUPPLÉMENTAIRES (décommentez si besoin)".center(80, "-"))
    
    # Test 1: Requête simple (devrait réussir rapidement)
    # test_simple = "Combien d'AS sont présents en France?"
    # logger.info(f"Test simple: {test_simple}")
    # result_simple = process_user_request_with_retry(test_simple)
    # pretty_print_result(result_simple)
    
    # Test 2: Requête impossible (pour tester la détection)
    # test_impossible = "Donne-moi la recette de la tarte aux pommes"
    # logger.info(f"Test impossible: {test_impossible}")
    # result_impossible = process_user_request_with_retry(test_impossible)
    # pretty_print_result(result_impossible)