### Analyse de l'Indicateur IRI

Cet indicateur, situé dans le pilier "Préparation du Marché", mesure le niveau de concentration du marché de l'accès à Internet dans un pays. Il utilise l'indice Herfindahl-Hirschman (HHI), qui est une mesure acceptée de la concurrence. Un score faible sur cet indicateur IRI suggère un marché dominé par un ou quelques acteurs (monopole/oligopole), ce qui nuit à la résilience en créant des dépendances excessives et en limitant le choix des consommateurs. Les entités techniques clés sont les **Systèmes Autonomes (`:AS`)** qui agissent en tant que fournisseurs d'accès, et leur part de marché respective, que l'IRI et YPI estiment via la population desservie.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Très Pertinent). Le schéma YPI intègre directement les données de "Population Estimates" d'APNIC, la source citée par l'IRI. La relation `(:AS)-[:POPULATION]->(:Country)` contient une propriété qui représente le pourcentage de la population d'un pays desservie par un AS, ce qui est une excellente approximation de la part de marché.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Lister la part de marché (population desservie) des AS d'un pays

* **Objectif de la requête :** Cette requête fondamentale établit la structure du marché. Elle identifie tous les fournisseurs d'accès (AS) opérant dans le pays cible et retourne leur part de marché estimée. Cela permet de visualiser immédiatement qui sont les acteurs dominants et quelle est la fragmentation du marché.

* **Requête Cypher :**
    ```cypher
    // Récupère la part de marché de chaque AS dans un pays donné.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'CI' pour la Côte d'Ivoire).
    MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
    // Récupère le nom de l'AS pour une meilleure lisibilité.
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    RETURN as.asn AS asn,
           n.name AS asName,
           p.population_percent AS marketSharePercent
    ORDER BY marketSharePercent DESC;
    ```

#### Requête 2 : Calculer directement l'indice de concentration du marché (HHI)

* **Objectif de la requête :** Cette requête va au-delà de la simple liste en calculant directement l'indice HHI, répliquant ainsi la méthodologie de l'IRI. L'indice est calculé en faisant la somme des carrés des parts de marché de chaque fournisseur. Un résultat élevé (proche de 10000) indique un monopole, tandis qu'un résultat faible (inférieur à 1500) suggère un marché concurrentiel.

* **Requête Cypher :**
    ```cypher
    // Calcule l'indice Herfindahl-Hirschman (HHI) pour un pays donné.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'CI').
    MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
    // Calcule la somme des carrés des parts de marché (en pourcentage).
    WITH sum(p.population_percent^2) AS hhi
    RETURN hhi,
        CASE
            WHEN hhi < 1500 THEN 'Marché Concurrentiel'
            WHEN hhi >= 1500 AND hhi <= 2500 THEN 'Marché Modérément Concentré'
            ELSE 'Marché Très Concentré'
        END AS marketConcentration;
    ```

### Objectif Global de l'Analyse

L'exécution de ces requêtes fournira une vue quantitative et sans ambiguïté de la concurrence sur le marché de l'internet d'un pays.

* **Compréhension :** Si un pays a un mauvais score IRI pour la "Concurrence sur le marché", la **Requête 1** identifiera immédiatement le ou les quelques AS qui dominent le marché. La **Requête 2** confirmera cette observation avec un score HHI élevé, expliquant ainsi techniquement la faiblesse de la résilience sur ce point. Nous ne nous contentons pas de savoir que le score est mauvais, nous savons *qui* sont les acteurs dominants et dans quelle proportion.

* **Amélioration :** Armé de ces données, il est possible d'engager des actions ciblées. Si l'analyse révèle un HHI élevé, cela constitue une preuve solide à présenter aux régulateurs nationaux pour argumenter en faveur de politiques pro-concurrentielles. Ces politiques pourraient inclure des mesures pour faciliter l'entrée de nouveaux acteurs, assurer un accès équitable aux infrastructures essentielles (fibre, pylônes), ou examiner les pratiques commerciales des opérateurs dominants. L'objectif est de diminuer la concentration pour augmenter la résilience, la qualité de service et l'abordabilité pour les utilisateurs finaux.