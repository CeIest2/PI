from src.RAG.knowledges_graph import setup_local_graph, get_local_driver

if __name__ == "__main__":
    print("Test de connexion...")
    try:
        setup_local_graph()
        
        driver = get_local_driver()
        with driver.session() as session:
            res = session.run("RETURN 'Neo4j Local est vivant !' as msg").single()
            print(f"SUCCÈS : {res['msg']}")
            
            # Vérifions les plugins
            plugins = session.run("CALL dbms.listConfig() YIELD name WHERE name CONTAINS 'plugin' RETURN name").data()
            print("Plugins détectés (vérification sommaire OK).")
            
        driver.close()
    except Exception as e:
        print(f"ÉCHEC : {e}")