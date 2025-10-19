from neo4j import GraphDatabase, exceptions
import logging

# URI pour se connecter à la base de données DOCKER LOCALE
# bolt:// -> Connexion directe non chiffrée (parfait pour le local)
# localhost:7687 -> L'adresse et le port standard de Neo4j
URI = "bolt://localhost:7687"

# AUTHENTIFICATION fournie par le README pour l'instance locale
AUTH = ("neo4j", "password")

# Votre requête
query = """
MATCH (c:Country {country_code: 'FR'})<-[pop:POPULATION]-(as:AS)
OPTIONAL MATCH (as)-[:NAME]->(n:Name)
OPTIONAL MATCH (as)-[:MEMBER_OF]->(m:Organization {name:"MANRS"})
RETURN
    as.asn AS asn,
    n.name AS name,
    pop.percent AS populationServedPercentage,
    (m IS NOT NULL) AS isManrsMember
ORDER BY populationServedPercentage DESC
LIMIT 10
"""

print("--- Connexion à la base de données IYP locale ---")

# Utiliser un 'driver' pour gérer la connexion
# Le bloc 'with' s'assure que la connexion est bien fermée à la fin
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    try:
        # Vérification de la connexion
        driver.verify_connectivity()
        print("Connexion réussie !")
        
        # Exécuter la requête et récupérer les résultats
        records, summary, keys = driver.execute_query(query)
        
        print("\n--- Top 10 des réseaux d'accès en France (par population) et statut MANRS ---")
        
        # Parcourir et afficher chaque enregistrement
        for record in records:
            manrs_status = "Oui" if record["isManrsMember"] else "Non"
            print(f"ASN: {record['asn']:<8} | Nom: {record['name']:<40} | Population desservie: {record['populationServedPercentage']:.2f}% | Membre MANRS: {manrs_status}")

    except exceptions.AuthError:
        logging.error("Erreur d'authentification : vérifiez le nom d'utilisateur et le mot de passe.")
    except exceptions.ServiceUnavailable as error:
        logging.error(f"Erreur de connexion : le conteneur Docker IYP est-il bien démarré ? Détails : {error}")
    except Exception as e:
        logging.error(f"Une erreur inattendue est survenue : {e}")