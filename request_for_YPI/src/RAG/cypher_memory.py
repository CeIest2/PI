import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Configuration du chemin de stockage persistant pour cette mémoire spécifique
MEMORY_DB_PATH = os.path.join("data", "cypher_memory_db")

class CypherMemory:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        # On utilise une collection séparée pour ne pas polluer le RAG documentaire
        self.vector_store = Chroma(
            persist_directory=MEMORY_DB_PATH,
            embedding_function=self.embeddings,
            collection_name="successful_cypher_queries"
        )

    def save_query(self, user_question, cypher_query, explanation="Valid query"):
        """
        Stocke une requête réussie.
        """
        # On formate le contenu pour qu'il soit lisible par le LLM lors de la récupération
        content_to_embed = f"QUESTION: {user_question}\nCYPHER_QUERY: {cypher_query}\nEXPLANATION: {explanation}"
        
        # On ajoute des métadonnées pour pouvoir filtrer si besoin
        metadata = {
            "type": "cypher_example",
            "question": user_question,
            "query": cypher_query
        }
        
        doc = Document(page_content=content_to_embed, metadata=metadata)
        self.vector_store.add_documents([doc])
        print(f"💾 Requête Cypher sauvegardée en mémoire pour : {user_question[:30]}...")

    def get_similar_examples(self, user_question, k=3):
        """
        Récupère les k exemples les plus proches sémantiquement.
        """
        try:
            results = self.vector_store.similarity_search(user_question, k=k)
            if not results:
                return ""
            
            # Formater les exemples pour le prompt
            formatted_examples = "\n\n".join([f"--- EXAMPLE {i+1} ---\n{doc.page_content}" for i, doc in enumerate(results)])
            return formatted_examples
        except Exception as e:
            print(f"⚠️ Erreur récupération mémoire Cypher : {e}")
            return ""

# Instance globale
cypher_memory = CypherMemory()  