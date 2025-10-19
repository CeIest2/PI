### Analyse de l'Indicateur IRI : Score de l'indice de développement de l'E-Gouvernement

Cet indicateur du pilier "Préparation du Marché" mesure la maturité des services publics numériques d'un pays, en se basant sur l'indice EGDI des Nations Unies. Un score élevé indique une forte présence et une grande qualité des services en ligne pour les citoyens. Les entités techniques clés sous-jacentes sont les `:DomainName` (portails gouvernementaux) et les `:AS` et `:Prefix` qui hébergent ces services.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Pertinent, avec une nuance). Le YPI ne contient pas le score EGDI lui-même, car c'est un indicateur composite externe. Cependant, le YPI est **extrêmement pertinent** pour analyser l'**infrastructure technique qui sous-tend ces services gouvernementaux**. Nous pouvons l'utiliser pour évaluer la résilience, la localisation et la sécurité de l'hébergement des portails e-gouvernement, ce qui influence directement la disponibilité et la performance de ces services.

Le plan consiste à d'abord identifier les domaines gouvernementaux potentiels, puis à analyser en profondeur leur infrastructure d'hébergement.

#### Requête 1 : Découvrir les domaines potentiellement gouvernementaux par popularité locale

* **Objectif de la requête :** Les services e-gouvernement sont souvent parmi les sites les plus consultés depuis l'intérieur d'un pays. Cette requête identifie les domaines les plus populaires se terminant par le ccTLD du pays, en se basant sur le pourcentage de requêtes DNS provenant de ce même pays. C'est un excellent point de départ pour repérer les portails nationaux majeurs.

* **Requête Cypher :**
    ```cypher
    // Trouve les domaines populaires sous le ccTLD d'un pays, classés par le % de requêtes locales.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})
    MATCH (d:DomainName)-[q:QUERIED_FROM]->(c)
    // Filtre pour les domaines se terminant par le ccTLD du pays (ex: '.sn')
    WHERE d.name ENDS WITH '.' + toLower($countryCode)
    // Utilise le rang Tranco comme critère de tri secondaire
    OPTIONAL MATCH (d)-[r:RANK]->(:Ranking {name:"Tranco top 1M"})
    RETURN d.name AS domainName,
           q.value AS percentageOfLocalQueries,
           r.rank AS trancoRank
    ORDER BY percentageOfLocalQueries DESC, trancoRank ASC
    LIMIT 25;
    ```

#### Requête 2 : Analyser l'infrastructure d'hébergement d'un domaine spécifique

* **Objectif de la requête :** Une fois qu'un domaine gouvernemental est identifié (grâce à la requête 1 ou par connaissance locale), cette requête permet de cartographier son infrastructure d'hébergement. Elle détermine sur quel(s) Système(s) Autonome(s) (AS) le domaine est hébergé et, de manière cruciale, si cet hébergement est local (dans le pays) ou à l'étranger. Ceci est fondamental pour évaluer la souveraineté numérique et la dépendance à des infrastructures externes.

* **Requête Cypher :**
    ```cypher
    // Analyse l'infrastructure d'hébergement pour un nom de domaine donné.
    // PARAMETRES : $domainName (ex: 'service-public.fr'), $countryCode (ex: 'FR').
    MATCH (d:DomainName {name: $domainName})
    // Trouve les IPs vers lesquelles le domaine se résout
    MATCH (d)-[:RESOLVES_TO]->(ip:IP)
    // Trouve le préfixe et l'AS d'origine
    MATCH (p:Prefix)-[:HAS_IP]->(ip)
    MATCH (hostingAS:AS)-[:ORIGINATE]->(p)
    // Récupère les informations sur l'AS d'hébergement (nom, pays)
    OPTIONAL MATCH (hostingAS)-[:NAME]->(n:Name)
    OPTIONAL MATCH (hostingAS)-[:COUNTRY]->(hostingCountry:Country)
    RETURN DISTINCT
           hostingAS.asn AS hostingASN,
           n.name AS hostingASName,
           hostingCountry.country_code AS hostingASCountry,
           // Compare le pays de l'AS au pays analysé
           (hostingCountry.country_code = $countryCode) AS isHostedLocally
    LIMIT 10;
    ```

#### Requête 3 : Évaluer la sécurité de routage de l'infrastructure e-gouvernement

* **Objectif de la requête :** Cette requête évalue la posture de sécurité de routage des AS qui hébergent les services gouvernementaux. En vérifiant le statut RPKI (Resource Public Key Infrastructure) des préfixes IP annoncés par ces AS, on peut déterminer si l'infrastructure est protégée contre le détournement de BGP (BGP hijacking), une attaque qui pourrait rendre les services e-gouvernement inaccessibles.

* **Requête Cypher :**
    ```cypher
    // Vérifie le statut RPKI des préfixes annoncés par un AS hébergeant un service gouvernemental.
    // PARAMETRE : $hostingASN (un ASN identifié avec la requête précédente, ex: 16276)
    MATCH (hostingAS:AS {asn: $hostingASN})-[:ORIGINATE]->(p:Prefix)
    MATCH (p)-[:CATEGORIZED]->(t:Tag)
    WHERE t.label STARTS WITH 'RPKI'
    RETURN t.label AS rpkiStatus,
           count(p) AS numberOfPrefixes
    ORDER BY numberOfPrefixes DESC;
    ```

### Objectif Global de l'Analyse

L'exécution de ces requêtes fournira une radiographie de l'infrastructure technique de l'e-gouvernement d'un pays.

* **Compréhension :** Les résultats nous diront si la stratégie numérique du gouvernement repose sur une infrastructure nationale ou si elle est déléguée à des hébergeurs et clouds internationaux. Un score EGDI élevé mais avec une infrastructure entièrement étrangère met en lumière une forte dépendance. Un score faible pourrait s'expliquer par un hébergement sur un petit nombre d'AS locaux, avec une mauvaise sécurité de routage (beaucoup de préfixes `RPKI NotFound` ou `Invalid`), constituant un risque technique important pour la continuité des services publics.

* **Amélioration :** Si l'analyse révèle que des portails critiques sont hébergés sur des AS locaux sans une bonne hygiène de routage (faible adoption RPKI/MANRS), une action corrective claire est de travailler avec les agences gouvernementales pour exiger de leurs fournisseurs le respect des standards de sécurité. Si tous les services sont hébergés à l'étranger, cela peut initier une discussion stratégique sur l'importance de développer un cloud gouvernemental ou souverain pour renforcer la résilience nationale et garder le contrôle sur les données des citoyens.