### Analyse de l'Indicateur IRI

Cet indicateur du pilier **"Préparation du Marché" (Market Readiness)** évalue la dépendance d'un pays à ses fournisseurs de transit Internet (amont). Un score faible suggère une forte dépendance à un petit nombre de fournisseurs, ce qui constitue un risque de point de défaillance unique (Single Point of Failure) et une faible résilience. Les entités techniques clés sont les `:AS` situés dans le pays et les `:AS` (souvent étrangers) qui leur fournissent du transit.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Très Pertinent) ✅. Le schéma YPI contient des données de topologie BGP (via BGPKIT) et de dépendance quantifiée (via IHR) qui permettent une analyse approfondie de cet indicateur.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Identifier les fournisseurs de transit (amont) par nombre de clients

* **Objectif de la requête :** Cette requête est la première étape fondamentale. Elle utilise les relations BGP pour identifier tous les fournisseurs de transit externes des réseaux (AS) du pays cible. Le but est de compter combien d'AS locaux dépendent de chaque fournisseur, révélant ainsi les acteurs les plus critiques du marché du transit pour ce pays en termes de part de marché.

* **Requête Cypher :**
    ```cypher
    // Identifie les fournisseurs de transit pour un pays donné et compte leurs clients locaux.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    // Utilise BGPKIT (r.rel=1) pour trouver les relations Provider-to-Customer.
    MATCH (as)-[r:PEERS_WITH {rel: 1}]->(provider:AS)
    // S'assure que le fournisseur n'est pas lui-même local (focus sur le transit international).
    WHERE NOT (provider)-[:COUNTRY]->(c)
    WITH provider, count(DISTINCT as) AS localCustomers
    // Récupère le nom du fournisseur pour une meilleure lisibilité.
    OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
    RETURN provider.asn AS providerASN,
           n.name AS providerName,
           localCustomers
    ORDER BY localCustomers DESC
    LIMIT 10;
    ```

#### Requête 2 : Analyser la force de la dépendance (Hégémonie)

* **Objectif de la requête :** Alors que la première requête compte les clients, celle-ci quantifie la **force** de la dépendance en utilisant la métrique d'hégémonie (`d.hege`) de l'IHR. Un score d'hégémonie élevé indique une dépendance critique. Cette requête permet de distinguer un fournisseur ayant beaucoup de petits clients d'un fournisseur dont dépendent les réseaux les plus importants du pays.

* **Requête Cypher :**
    ```cypher
    // Mesure la dépendance moyenne des AS d'un pays envers leurs fournisseurs de transit.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    // Utilise la relation de dépendance et la métrique d'hégémonie de l'IHR.
    MATCH (as)-[d:DEPENDS_ON]->(provider:AS)
    // Filtre pour les dépendances significatives afin de réduire le bruit.
    WHERE d.hege > 0.1 AND NOT (provider)-[:COUNTRY]->(c)
    WITH provider, avg(d.hege) AS averageHegemony, count(DISTINCT as) AS dependentASNs
    OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
    RETURN provider.asn AS providerASN,
           n.name AS providerName,
           averageHegemony,
           dependentASNs
    ORDER BY averageHegemony DESC, dependentASNs DESC
    LIMIT 10;
    ```

### Objectif Global de l'Analyse (Compréhension et Amélioration)

L'exécution de ces deux requêtes pour un pays donné fournira une vision technique précise de sa diversité de transit.

* **Compréhension 🧐 :** La **Requête 1** identifiera les fournisseurs dominants en termes de nombre de clients. La **Requête 2** confirmera si cette dominance se traduit par une dépendance technique critique (hégémonie élevée). Si un même `providerASN` apparaît en tête des deux listes avec des scores élevés, cela matérialise le risque théorique mesuré par l'IRI. Nous aurons identifié un point de défaillance unique ou un oligopole de transit.

* **Amélioration 💡 :** Fort de ces données, une action concrète serait de lancer un programme de diversification. Cela pourrait inclure des subventions ou des formations pour encourager les AS locaux à se connecter à d'autres fournisseurs de transit (Tier-1/Tier-2). De manière plus stratégique, cela pourrait motiver le renforcement de l'écosystème de peering local (voir l'indicateur "Efficacité du peering") pour que le trafic local reste local et ne dépende pas de ces fournisseurs de transit internationaux.