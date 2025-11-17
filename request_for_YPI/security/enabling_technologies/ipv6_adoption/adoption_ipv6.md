### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Sécurité" est un score composite de haut niveau, l'Indice Mondial de Cybersécurité (GCI) de l'Union Internationale des Télécommunications (UIT). Il mesure l'engagement d'un pays en matière de cybersécurité sur la base de cinq piliers : les mesures juridiques, les mesures techniques, les mesures organisationnelles, le renforcement des capacités et la coopération.

Les "entités" impliquées ne sont pas des objets techniques discrets présents dans un graphe réseau (comme des AS ou des préfixes), mais plutôt des concepts et des structures nationaux (lois, agences de cybersécurité, programmes de formation, etc.).

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas B (Non-Pertinent).

L'Indice Mondial de Cybersécurité est une mesure politique et organisationnelle issue de sources externes (UIT) qui ne sont pas modélisées dans le schéma YPI. Le graphe YPI se concentre sur la topologie technique et les relations opérationnelles d'Internet (relations BGP, RPKI, membres d'IXP, etc.). Il ne contient aucune donnée relative à des scores d'indices politiques ou légaux.

Par conséquent, il est impossible de créer une requête Cypher pour interroger ou analyser directement cet indicateur à l'aide des données disponibles dans YPI.

---

## Analyses Complémentaires (Sécurité du Routage et Adoption IPv6)

Bien que l'indicateur GCI spécifique (un score politique) ne soit pas modélisé dans YPI, d'autres indicateurs techniques fondamentaux liés à la sécurité du routage et à l'adoption d'IPv6 peuvent être analysés.

---

### Requête 1 : Pourcentage de Préfixes IPv6

* **Objectif de la requête :** Calcule le pourcentage de préfixes BGP annoncés par les AS d'un pays qui sont des préfixes IPv6 (par opposition à IPv4). Cela donne une mesure de l'adoption d'IPv6 au niveau du routage.

* **Requête Cypher :**
    ```cypher
    // Calcule le pourcentage d'AS dans un pays qui annoncent des préfixes IPv6.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
    MATCH (c:Country {country_code: countryCode})
    
    // Trouver tous les préfixes BGP originaires d'AS de ce pays
    MATCH (as:AS)-[:COUNTRY]->(c)
    MATCH (as)-[:ORIGINATE]->(p:BGPPrefix)
    
    // Compter le total, et compter ceux qui sont IPv6 (af = 6)
    WITH c, 
         count(p) AS totalPrefixes,
         count(CASE WHEN p.af = 6 THEN p ELSE null END) AS ipv6Prefixes,
         count(CASE WHEN p.af = 4 THEN p ELSE null END) AS ipv4Prefixes
    
    // Calculer le pourcentage
    RETURN c.name AS pays,
           totalPrefixes,
           ipv4Prefixes,
           ipv6Prefixes,
           CASE 
               WHEN totalPrefixes = 0 THEN 0 
               ELSE (toFloat(ipv6Prefixes) / totalPrefixes) * 100.0 
           END AS pourcentagePrefixesIPv6
    ORDER BY pourcentagePrefixesIPv6 DESC
    ```

---

### Requête 2 : Identification des AS sans Annonce IPv6

* **Objectif de la requête :** Identifie les AS importants (classés par taille de cône client) dans un pays qui n'annoncent *aucun* préfixe IPv6. Cela permet de cibler les efforts d'adoption d'IPv6 sur les acteurs ayant le plus d'impact.

* **Requête Cypher :**
    ```cypher
    // Identifie les AS d'un pays sans annonce IPv6, classés par importance.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    
    // Vérifie l'existence d'annonces IPv6 pour cet AS.
    OPTIONAL MATCH (as)-[:ORIGINATE]->(p:Prefix)
    WHERE p.prefix CONTAINS ':'
    
    WITH as, count(p) AS ipv6PrefixCount
    // Garde uniquement les AS qui n'ont AUCUNE annonce IPv6.
    WHERE ipv6PrefixCount = 0
    
    // Récupère le rang et la taille du cône client pour évaluer l'importance de l'AS.
    MATCH (as)-[r:RANK]->(rank:Ranking {name:'CAIDA ASRank'})
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    
    RETURN
        as.asn AS asn,
        n.name AS name,
        r['cone:numberAsns'] AS customerConeSize
    ORDER BY customerConeSize DESC
    LIMIT 15;
    ```