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

---

### Requête 3 : Disponibilité IPv6 de l'Infrastructure DNS

* **Objectif de la requête :** Évalue l'adoption d'IPv6 au sein de l'infrastructure DNS critique (serveurs faisant autorité et résolveurs) localisée dans le pays.

* **Requête Cypher :**
    ```cypher
    // 3. Disponibilité IPv6 de l'infrastructure DNS
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
    MATCH (c:Country {country_code: countryCode})
    
    // 1. Compter les serveurs faisant autorité accessibles en IPv6
    MATCH (ans:AuthoritativeNameServer)<-[:ALIAS_OF]-(h_ans:HostName)-[:RESOLVES_TO]->(ip_ans:IP)
    MATCH (ip_ans)-[:PART_OF]->(p_ans)
    MATCH (p_ans)-[:COUNTRY]->(c)
    WITH c, 
         count(DISTINCT ans) AS totalANS,
         count(DISTINCT CASE WHEN ip_ans.af = 6 THEN ans ELSE null END) AS ipv6ReadyANS
    
    // 2. Compter les résolveurs accessibles en IPv6
    MATCH (res:Resolver)<-[:RESOLVES_TO]-(h_res:HostName)-[:RESOLVES_TO]->(ip_res:IP)
    MATCH (ip_res)-[:PART_OF]->(p_res)
    MATCH (p_res)-[:COUNTRY]->(c)
    WITH c, totalANS, ipv6ReadyANS,
         count(DISTINCT res) AS totalResolvers,
         count(DISTINCT CASE WHEN ip_res.af = 6 THEN res ELSE null END) AS ipv6ReadyResolvers
    
    // 3. Retourner les résultats
    RETURN c.name AS pays,
           totalANS,
           ipv6ReadyANS,
           totalResolvers,
           ipv6ReadyResolvers
    ```

---

### Requête 4 : Taux de Serveurs (HostName) Dual-Stack

* **Objectif de la requête :** Calcule le pourcentage de serveurs (identifiés par leur `HostName`) dans un pays qui sont accessibles à la fois en IPv4 et en IPv6 (dual-stack), ainsi que ceux qui sont uniquement accessibles en IPv6.

* **Requête Cypher :**
    ```cypher
    // 2. Taux de serveurs (HostName) Dual-Stack (IPv4 + IPv6)
    
    MATCH (c:Country {country_code: countryCode})
    
    // 1. Trouver tous les serveurs (HostName) localisés dans ce pays
    MATCH (h:HostName)-[:RESOLVES_TO]->(ip:IP)
    MATCH (ip)-[:PART_OF]->(p)
    MATCH (p)-[:COUNTRY]->(c)
    WITH c, h // Obtenir les HostName uniques
    
    // 2. Pour chaque HostName, collecter toutes les familles d'adresses (4 ou 6)
    MATCH (h)-[:RESOLVES_TO]->(ip_check:IP)
    WITH c, h, collect(DISTINCT ip_check.af) AS addressFamilies
    
    // 3. Compter
    WITH c, 
         count(h) AS totalServers,
         count(CASE 
             // Doit avoir 4 ET 6 dans sa liste d'AF
             WHEN (4 IN addressFamilies) AND (6 IN addressFamilies) THEN h 
             ELSE null 
         END) AS dualStackServers,
         count(CASE 
             // N'a que du 6
             WHEN NOT (4 IN addressFamilies) AND (6 IN addressFamilies) THEN h 
             ELSE null 
         END) AS ipv6OnlyServers
    
    // 4. Calculer le pourcentage
    RETURN c.name AS pays,
           totalServers,
           dualStackServers,
           ipv6OnlyServers,
           CASE 
               WHEN totalServers = 0 THEN 0 
               ELSE (toFloat(dualStackServers) / totalServers) * 100.0 
           END AS pourcentageDualStack
    ORDER BY pourcentageDualStack DESC
    ```