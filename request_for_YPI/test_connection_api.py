# debug_connections.py
import os
from pathlib import Path
from dotenv import load_dotenv
from request_for_YPI.src.utils.loaders import load_text_file
from src.utils.llm import get_llm
from src.request_IYP.request_testing import execute_cypher_test
from src.RAG.knowledges_graph import get_local_driver, setup_local_graph
from src.utils.logger import logger

# Chargement du .env
load_dotenv()

def test_environment():
    logger.section("1. Vérification de l'Environnement")
    
    # API LLM
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        logger.success(f"✅ Clé GOOGLE_API_KEY détectée ({api_key[:5]}...)")
    else:
        logger.error("❌ Clé GOOGLE_API_KEY manquante")

    # Neo4j Distant (IYP)
    if os.getenv("NEO4J_PASSWORD"):
        logger.success("✅ Identifiants Neo4j Distant détectés")
    else:
        logger.warning("⚠️ Identifiants Neo4j Distant (PASSWORD) manquants (OK si Bolt sans auth)")

    # Neo4j Local (RAG)
    logger.info(f"📍 URI Local configuré : {os.getenv('NEO4J_LOCAL_URI', 'bolt://172.22.32.1:7687')}")

def test_llm_connection():
    logger.section("2. Test Connexion LLM (Gemini)")
    try:
        llm = get_llm("fast") 
        response = llm.invoke("Réponds 'OK'.")
        if "OK" in response.content.upper():
            logger.success("✅ Connexion au LLM réussie.")
    except Exception as e:
        logger.error(f"❌ Échec LLM : {str(e)}")

def test_neo4j_remote():
    logger.section("3. Test Neo4j Distant (Données IYP)")
    test_query = "RETURN 'Connexion distante OK' as msg LIMIT 1"
    result = execute_cypher_test(test_query)
    
    if result["success"]:
        logger.success(f"✅ Neo4j Distant est accessible.")
    else:
        logger.error(f"❌ Échec Neo4j Distant : {result['error']}")

def test_neo4j_local_rag():
    logger.section("4. Test Neo4j Local (RAG)")
    try:
        # Utilisation de votre fonction get_local_driver
        driver = get_local_driver()
        
        with driver.session() as session:
            # Test de réactivité simple
            res = session.run("RETURN 'Connexion locale OK' as msg").single()
            logger.success(f"✅ Neo4j Local est vivant : {res['msg']}")
            
            # Vérification de l'index vectoriel pour le RAG
            logger.info("🔍 Vérification de l'index RAG...")
            index_check = session.run("SHOW VECTOR INDEXES WHERE name = 'chunk_vector_index'").data()
            if index_check:
                logger.success("✅ Index vectoriel 'chunk_vector_index' détecté.")
            else:
                logger.warning("⚠️ Index RAG manquant. Tentative d'initialisation...")
                setup_local_graph() #
                
        driver.close()
    except Exception as e:
        logger.error(f"❌ Échec Neo4j Local (RAG) : {str(e)}")
        logger.info("💡 Vérifiez que votre instance Neo4j locale est lancée (Docker ou Desktop).")



def generate_final_report_part(country_name, section_name, investigation_findings, mode="reasoning"):
    """
    Génère la section finale du rapport en Markdown en synthétisant les découvertes.
    Utilise strictement les fonctions et variables définies dans le script.
    """
    logger.info(f"📝 Synthèse finale de la section : {section_name} ({country_name})")

    investigation_context = ""
    for item in investigation_findings:
        investigation_context += f"### QUESTION: {item['question']}\n"
        investigation_context += f"### ANSWER:\n{item['answer']}\n"
        investigation_context += "-" * 30 + "\n\n"


    render_prompt_path = os.path.join(SYSTEM_PROMPT_DIR, "render_document_thinking.txt")
    
    try:
        render_template = load_text_file(render_prompt_path)
        

        final_prompt = (
            render_template
            .replace("[COUNTRY_NAME]", country_name)
            .replace("{{SECTION_NAME}}", section_name)
            .replace("{{INVESTIGATION_FINDINGS}}", investigation_context)
        )


        return run_llm_step(final_prompt, mode=mode)
        
    except Exception as e:
        logger.error(f"❌ Échec de la synthèse finale pour {section_name} : {str(e)}")
        return f"Error: {str(e)}"


if __name__ == "__main__":
    print("\n🚀 Lancement du diagnostic complet des services...\n")
    
    test_environment()
    test_llm_connection()
    test_neo4j_remote()
    test_neo4j_local_rag()
    
    print("\n🏁 Diagnostic terminé.")