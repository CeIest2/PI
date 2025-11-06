### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Sécurité" est un score composite de haut niveau, l'Indice Mondial de Cybersécurité (GCI) de l'Union Internationale des Télécommunications (UIT). Il mesure l'engagement d'un pays en matière de cybersécurité sur la base de cinq piliers : les mesures juridiques, les mesures techniques, les mesures organisationnelles, le renforcement des capacités et la coopération.

Les "entités" impliquées ne sont pas des objets techniques discrets présents dans un graphe réseau (comme des AS ou des préfixes), mais plutôt des concepts et des structures nationaux (lois, agences de cybersécurité, programmes de formation, etc.).

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas B (Non-Pertinent).

L'Indice Mondial de Cybersécurité est une mesure politique et organisationnelle issue de sources externes (UIT) qui ne sont pas modélisées dans le schéma YPI. Le graphe YPI se concentre sur la topologie technique et les relations opérationnelles d'Internet (relations BGP, RPKI, membres d'IXP, etc.). Il ne contient aucune donnée relative à des scores d'indices politiques ou légaux.

Par conséquent, il est impossible de créer une requête Cypher pour interroger ou analyser directement cet indicateur à l'aide des données disponibles dans YPI.

---

## Analyses Complémentaires (Indicateurs MANRS et Connectivité)

Bien que l'indicateur GCI spécifique (un score politique) ne soit pas modélisé dans YPI, d'autres indicateurs techniques fondamentaux liés à la sécurité du routage et à la coordination (alignés sur les principes MANRS) peuvent être analysés. Voici les requêtes pour ces mesures :

### Requête 1 : Taux d'adoption RPKI par pays (Indicateur MANRS)

* [cite_start]**Objectif de la requête :** Calcule le pourcentage de préfixes IP (routes) originaires d'un pays qui sont sécurisés par RPKI (Resource Public Key Infrastructure)[cite: 6]. Un taux élevé est un signe de bonne hygiène de routage pour prévenir les détournements de route.

* **Requête Cypher :**
    ```cypher
    // 1. Taux d'adoption RPKI par pays (Indicateur MANRS)
    
    // 1. Trouver tous les préfixes BGP pour un pays
    MATCH (c:Country {country_code: countryCode})
    // HYPOTHÈSE: (AS)-[:COUNTRY]->(Country)
    MATCH (as:AS)-[:COUNTRY]->(c) 
    // HYPOTHÈSE: (AS)-[:ORIGINATE]->(BGPPrefix)
    MATCH (as)-[:ORIGINATE]->(p:BGPPrefix)
    WITH c, count(DISTINCT p) AS totalPrefixes
    
    // 2. Compter ceux qui sont couverts par RPKI
    MATCH (c)<-[:COUNTRY]-(as_covered:AS)-[:ORIGINATE]->(p_covered:BGPPrefix)
    // HYPOTHÈSE: (BGPPrefix)<-[:RESOLVES_TO]-(RPKIPrefix)
    MATCH (p_covered)<-[:PART_OF]-(:RPKIPrefix)
    WITH c, totalPrefixes, count(DISTINCT p_covered) AS totalCoveredPrefixes
    
    // 3. Calculer le pourcentage
    RETURN c.name AS pays,
           totalPrefixes,
           totalCoveredPrefixes,
           CASE 
               WHEN totalPrefixes = 0 THEN 0 
               ELSE (toFloat(totalCoveredPrefixes) / totalPrefixes) * 100.0 
           END AS pourcentageAdoptionRPKI
    ORDER BY pourcentageAdoptionRPKI DESC
    ```
    [cite_start][cite: 6, 7]

---

### Requête 2 : Taux de présence sur PeeringDB (Indicateur MANRS)

* [cite_start]**Objectif de la requête :** Évalue la coordination de l'écosystème en calculant le pourcentage d'AS d'un pays qui ont une entrée dans PeeringDB[cite: 1]. Une présence élevée facilite l'interconnexion et la résolution de problèmes.

* **Requête Cypher :**
    ```cypher
    // 2. Taux de présence sur PeeringDB (Indicateur MANRS)
    WITH 'FR' AS countryCode
    
    MATCH (c:Country {country_code: countryCode})
    MATCH (as:AS)-[:COUNTRY]->(c)
    WITH c, collect(DISTINCT as) AS allASes
    
    // Démêler et vérifier la présence d'un ID PeeringDB
    UNWIND allASes AS as
    // HYPOTHÈSE: (AS)-[:EXTERNAL_ID]->(PeeringdbNetID)
    // Vous devrez peut-être changer :PeeringdbNetID par :PeeringdbOrgID
    OPTIONAL MATCH (as)-[:EXTERNAL_ID]->(pdb:PeeringdbNetID) 
    
    WITH c, 
         count(as) AS totalAS,
         count(pdb) AS asAvecPeeringDB // Compte les AS qui ont un lien vers un ID PDB
    
    // Calculer le pourcentage
    RETURN c.name AS pays,
           totalAS,
           asAvecPeeringDB,
           CASE 
               WHEN totalAS = 0 THEN 0 
               ELSE (toFloat(asAvecPeeringDB) / totalAS) * 100.0 
           END AS pourcentageCoordination
    ORDER BY pourcentageCoordination DESC
    ```
    [cite_start][cite: 1, 2]

---

### Requête 3 : Concentration des Fournisseurs en Amont

* [cite_start]**Objectif de la requête :** Identifie les principaux points de dépendance externe en listant les fournisseurs de transit étrangers (peers) qui sont connectés au plus grand nombre d'AS domestiques[cite: 9].

* **Requête Cypher :**
    ```cypher
    // 2. Concentration des fournisseurs en amont
    
    // 1. Trouver les AS du pays et leurs peers externes
    MATCH (c:Country {country_code: countryCode})<-[:COUNTRY]-(as_fr:AS)
    MATCH (as_fr)-[:PEERS_WITH]-(peer:AS)
    MATCH (peer)-[:COUNTRY]->(peer_country:Country)
    WHERE peer_country <> c
    
    // 2. Regrouper par peer externe et compter les AS domestiques connectés
    RETURN peer.asn AS upstreamAS, 
           peer_country.country_code AS upstreamCountry,
           count(DISTINCT as_fr) AS clientsDomestiquesConnectes
    ORDER BY clientsDomestiquesConnectes DESC
    LIMIT 10
    ```
    [cite_start][cite: 9]