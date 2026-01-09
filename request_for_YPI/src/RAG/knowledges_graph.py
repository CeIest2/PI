# src/tools/knowledge_graph.py
import os
from neo4j import GraphDatabase
from src.utils.logger import logger

# Configuration Locale (Idéalement à mettre dans .env)
# Pour l'instant on hardcode pour tester, mais pensez à .env plus tard
URI_LOCAL = os.getenv("NEO4J_LOCAL_URI", "bolt://172.22.32.1:7687")
AUTH_LOCAL = (
    os.getenv("NEO4J_LOCAL_USER", "neo4j"),
    os.getenv("NEO4J_LOCAL_PASSWORD", "motdepasse")
)

VECTOR_INDEX_NAME = "chunk_vector_index"
VECTOR_DIMENSIONS = 768

def get_local_driver():
    """Crée une connexion vers l'instance Neo4j locale."""
    try:
        driver = GraphDatabase.driver(URI_LOCAL, auth=AUTH_LOCAL)
        driver.verify_connectivity()
        return driver
    except Exception as e:
        logger.error(f"Impossible de se connecter à Neo4j Local: {e}")
        raise e

def setup_local_graph():
    """Initialise le schéma et les index nécessaires."""
    driver = get_local_driver()
    with driver.session() as session:
        # 1. Contrainte d'unicité sur les URLs
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.url IS UNIQUE")
        
        # 2. Création de l'Index Vectoriel
        check_index_query = "SHOW VECTOR INDEXES WHERE name = $name"
        result = session.run(check_index_query, name="chunk_vector_index").data()
        
        if not result:
            logger.info("Création de l'index vectoriel 'chunk_vector_index'...")
            create_index_query = f"""
            CREATE VECTOR INDEX chunk_vector_index IF NOT EXISTS
            FOR (c:Chunk) ON (c.embedding)
            OPTIONS {{indexConfig: {{
                `vector.dimensions`: {VECTOR_DIMENSIONS},
                `vector.similarity_function`: 'cosine'
            }}}}
            """
            try:
                session.run(create_index_query)
                logger.info("Index vectoriel créé avec succès.")
            except Exception as e:
                logger.error(f"Erreur création index vectoriel: {e}")
        else:
            logger.debug("L'index vectoriel existe déjà.")
    
    driver.close()

def store_document_with_chunks(doc_data: dict, chunks: list):
    """
    Stocke un document et ses chunks vectorisés.
    """
    driver = get_local_driver()
    
    # --- CORRECTION DE LA REQUÊTE CYPHER ICI ---
    # Ajout du WITH c, d, chunk_data entre CREATE et CALL
    query = """
    MERGE (d:Document {url: $doc.url})
    SET d.title = $doc.title,
        d.summary = $doc.summary,
        d.type = $doc.type,
        d.updated_at = datetime()

    WITH d
    UNWIND $chunks AS chunk_data
    
    CREATE (c:Chunk {
        text: chunk_data.text, 
        index: chunk_data.chunk_index
    })
    
    WITH c, d, chunk_data
    CALL db.create.setNodeVectorProperty(c, 'embedding', chunk_data.embedding)
    
    MERGE (d)-[:CONTAINS]->(c)
    """
    
    try:
        with driver.session() as session:
            session.run(query, doc=doc_data, chunks=chunks)
            logger.info(f"Document stocké : {doc_data['url']} avec {len(chunks)} chunks.")
    except Exception as e:
        logger.error(f"Erreur lors du stockage dans Neo4j Local: {e}")
        raise e
    finally:
        driver.close()

def is_source_in_rag(url: str) -> bool:
    """
    Vérifie si une source (URL) est déjà présente dans le RAG.
    """
    driver = get_local_driver()
    try:
        with driver.session() as session:
            query = "MATCH (d:Document {url: $url}) RETURN d LIMIT 1"
            result = session.run(query, url=url).single()
            return result is not None
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la source dans Neo4j Local: {e}")
        return False
    finally:
        driver.close()