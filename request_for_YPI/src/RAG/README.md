# 🧠 RAG & Knowledge Graph - Installation Guide

Ce module gère la mémoire à long terme (RAG) de l'application en stockant les documents scrapés et leurs vecteurs (Embeddings) dans une base de données **Neo4j**.

## 📋 Prérequis

* **Docker** (Recommandé) OU **Neo4j Desktop**
* Python 3.10+
* Une clé API Google (pour les embeddings `text-embedding-004`)

---

## 🛠️ Option 1 : Installation via Docker (Recommandé)

C'est la méthode la plus simple. Elle installe automatiquement Neo4j avec les plugins nécessaires (**APOC** et **Graph Data Science**).

1.  Créez un fichier `docker-compose.yml` à la racine du projet avec ce contenu :

    ```yaml
    version: '3.8'

    services:
      neo4j-local:
        image: neo4j:5.15.0
        container_name: iyp_knowledge_graph
        ports:
          - "7474:7474" # HTTP (Browser)
          - "7687:7687" # Bolt (Connection Python)
        environment:
          - NEO4J_AUTH=neo4j/password_local_123
          - NEO4J_PLUGINS=["apoc", "graph-data-science"]
          - NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.*
          - NEO4J_server_memory_heap_initial__size=1G
          - NEO4J_server_memory_heap_max__size=2G
        volumes:
          - ./data/neo4j_data:/data
        restart: unless-stopped
    ```

2.  Lancez le conteneur :
    ```bash
    docker-compose up -d
    ```

3.  Accédez à l'interface : [http://localhost:7474](http://localhost:7474)
    * **User :** `neo4j`
    * **Password :** `password_local_123`

---

## 🖥️ Option 2 : Installation via Neo4j Desktop

Si vous ne pouvez pas utiliser Docker :

1.  Téléchargez et installez **Neo4j Desktop**.
2.  Créez une nouvelle base de données (Local DBMS).
3.  **IMPORTANT :** Installez les plugins requis via l'onglet "Plugins" :
    * ✅ **APOC**
    * ✅ **Graph Data Science Library** (GDS)
4.  Démarrez la base ("Start").

---

## ⚙️ Configuration (.env)

Ajoutez les variables suivantes à votre fichier `.env` pour que le code Python puisse se connecter :

```ini
# --- NEO4J LOCAL (RAG) ---
# Si Docker ou Desktop natif :
NEO4J_LOCAL_URI=bolt://localhost:7687

# ⚠️ SI VOUS ÊTES SUR WSL (Windows Subsystem for Linux) :
# Utilisez l'IP de Windows (trouvée via `ip route` dans WSL) au lieu de localhost
# NEO4J_LOCAL_URI=bolt://192.168.x.x:7687

NEO4J_LOCAL_USER=neo4j
NEO4J_LOCAL_PASSWORD=motdepasse

# --- EMBEDDINGS ---
# Requis pour la vectorisation
GOOGLE_API_KEY=votre_cle_api_google_ici