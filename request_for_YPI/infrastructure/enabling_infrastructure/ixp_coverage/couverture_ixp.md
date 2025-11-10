### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Infrastructure" évalue la disponibilité des Points d'Échange Internet (IXP) au sein d'un pays, en particulier par rapport à ses grands centres de population. Un score élevé signifie que l'infrastructure critique permettant de conserver le trafic Internet local et d'améliorer la performance est présente là où elle est le plus nécessaire. Les entités techniques clés sont les **:IXP**, les **:AS** (en tant que membres), les **:Facility** (où les IXP sont hébergés) et le **:Country**.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Très Pertinent, avec une limitation). Le schéma YPI, grâce aux données de PeeringDB, fournit des informations exhaustives sur les IXP, leurs membres et leurs localisations physiques (data centers). Il permet une analyse en profondeur de la santé de l'écosystème d'échange de trafic d'un pays. **Limitation :** YPI ne contient pas de données démographiques ou géographiques au niveau des villes. Par conséquent, il ne peut pas directement corréler la présence d'un IXP avec un "centre de population de plus de 300 000 habitants". Cependant, en analysant l'existence, le nombre et la vitalité des IXP, nous pouvons établir une base technique solide qui explique en grande partie le score de cet indicateur.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Inventaire des IXP et de leur localisation physique

* **Objectif de la requête :** La première étape consiste à vérifier l'existence même d'IXP dans le pays cible. Cette requête liste tous les IXP déclarés et, de manière cruciale, les centres de données (:Facility) où ils sont physiquement présents. Cela donne une première idée de la distribution géographique de cette infrastructure critique.

* **Requête Cypher :**
    ```cypher
    // Liste les IXP d'un pays et les data centers où ils sont situés.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (i:IXP)<-[:MEMBER_OF]-(a:AS)-[:LOCATED_IN]->(f:Facility),
      (a)-[:COUNTRY]->(c:Country {country_code: $countryCode})
    RETURN i.name AS IXP, COLLECT(DISTINCT f.name) AS Facilities
    ORDER BY SIZE(Facilities) DESC;
    ```

#### Requête 2 : Mesurer la vitalité des IXP par le nombre de membres

* **Objectif de la requête :** Un IXP n'est utile que si les réseaux s'y connectent. Cette requête mesure la vitalité de chaque IXP en comptant le nombre de membres (AS) locaux et internationaux. Un nombre élevé de membres locaux est le signe d'un écosystème de peering national sain, ce qui est l'objectif principal d'un IXP pour la résilience.

* **Requête Cypher :**
    ```cypher
    // Compte les membres locaux et internationaux pour chaque IXP d'un pays.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (i:IXP)<-[:MEMBER_OF]-(a:AS)-[:COUNTRY]->(c:Country)
    WITH i, c, a, (CASE WHEN c.country_code = $countryCode THEN 1 ELSE 0 END) AS local
    WHERE c.country_code IS NOT NULL
    RETURN i.name AS IXP,
        SUM(local) AS LocalMembers,
        COUNT(DISTINCT a) - SUM(local) AS ForeignMembers
    ORDER BY LocalMembers DESC;
    ```

#### Requête 3 : Identifier les principaux réseaux internationaux présents sur les IXP

* **Objectif de la requête :** La valeur d'un IXP augmente de manière exponentielle lorsqu'il attire de grands fournisseurs de contenu (CDN, Cloud, etc.). Leur présence permet de servir le contenu populaire localement, réduisant ainsi la latence et la dépendance au transit international. Cette requête identifie les réseaux internationaux les plus importants (selon le classement CAIDA AS Rank) connectés aux IXP du pays.

* **Requête Cypher :**
    ```cypher
    // Trouve les réseaux internationaux les mieux classés présents sur les IXP d'un pays.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (i:IXP)<-[:MEMBER_OF]-(a:AS)-[:COUNTRY]->(c:Country)
    WHERE c.country_code <> $countryCode
    AND EXISTS {
        MATCH (a2:AS)-[:COUNTRY]->(c2:Country {country_code: $countryCode})
        MATCH (a2)-[:MEMBER_OF]->(i)
    }
    OPTIONAL MATCH (a)-[:RANK]->(r:Ranking)
    RETURN a.asn AS ASN, i.name AS IXP, r.name AS Rank
    ORDER BY r.name ASC
    LIMIT 10;
        ```

### Objectif Global de l'Analyse

L'exécution de ces requêtes fournira une vue d'ensemble technique de l'écosystème d'échange de trafic du pays, ce qui est le fondement de l'indicateur IRI "Couverture des IXP".

* **Compréhension :** Si un pays a un mauvais score, ces requêtes en révéleront la raison technique.
    * La **Requête 1** pourrait ne retourner aucun résultat, indiquant une absence totale d'IXP.
    * La **Requête 2** pourrait montrer des IXP existants mais avec très peu de membres, en particulier locaux, ce qui signifie que l'infrastructure est sous-utilisée et que son impact sur la résilience est faible.
    * La **Requête 3** pourrait révéler l'absence de grands fournisseurs de contenu internationaux, indiquant que même si les acteurs locaux échangent du trafic entre eux, le trafic le plus demandé (vidéo, cloud) doit toujours être récupéré via des liaisons de transit coûteuses et moins performantes.

* **Amélioration :** Les résultats orientent directement vers des actions concrètes.
    * **Absence d'IXP :** L'action prioritaire est de lancer une initiative nationale pour créer un premier IXP, en rassemblant les opérateurs locaux et en cherchant le soutien des pouvoirs publics et d'organisations comme l'Internet Society.
    * **IXP sous-utilisé :** Il faut mener une campagne de sensibilisation et d'incitation auprès des opérateurs de réseaux locaux pour qu'ils rejoignent l'IXP. Cela peut inclure des formations sur les avantages techniques et économiques du peering et la simplification des procédures de connexion.
    * **Absence de contenu majeur :** L'opérateur de l'IXP et la communauté technique locale (NOG) peuvent engager un dialogue stratégique avec les grands CDN et fournisseurs de cloud, en leur présentant la valeur du marché local (nombre d'utilisateurs) pour les inciter à installer un cache local et à se connecter à l'IXP.
    