### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Sécurité" mesure le déploiement des extensions de sécurité du système de noms de domaine (DNSSEC). L'objectif de DNSSEC est de garantir l'authenticité et l'intégrité des réponses DNS en ajoutant des signatures cryptographiques. Un taux d'adoption élevé signifie que les noms de domaine pertinents pour le pays sont protégés contre des attaques comme l'empoisonnement du cache DNS (DNS cache poisoning) ou l'usurpation. Les entités techniques clés sont les `:DomainName`, les `:AS` et les `:Country`.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Partiellement Pertinent). Le schéma YPI ne contient pas de propriété directe indiquant si un domaine est signé avec DNSSEC. Par conséquent, YPI ne peut pas *directement* calculer un score d'adoption. Cependant, YPI est extrêmement pertinent pour une analyse en deux étapes : il peut d'abord identifier les domaines les plus critiques et les plus pertinents pour un pays donné. Ces listes de domaines peuvent ensuite être analysées avec un outil externe pour vérifier leur statut DNSSEC. Les requêtes suivantes servent à générer ces listes cibles.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Identifier les domaines les plus populaires consultés depuis le pays

* **Objectif de la requête :** Cette requête identifie les noms de domaine les plus fréquemment résolus par les utilisateurs à l'intérieur du pays cible, en utilisant les données de Cloudflare Radar. La protection de ces domaines est la plus critique pour la sécurité des internautes du pays, car ce sont les services qu'ils utilisent le plus. Une faible adoption de DNSSEC sur cette liste expose une grande partie de la population à des risques.

* **Requête Cypher :**
    ```cypher
    // Récupère les 25 domaines les plus populaires pour un pays donné, basés sur le % de requêtes DNS.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)
    RETURN d.name AS domainName,
           q.value AS queryPercentage
    ORDER BY queryPercentage DESC
    LIMIT 25;
    ```

#### Requête 2 : Identifier les domaines populaires hébergés dans le pays

* **Objectif de la requête :** Cette requête identifie les domaines populaires (classés par Tranco) qui sont hébergés localement, c'est-à-dire dont les adresses IP sont annoncées par des systèmes autonomes (AS) situés dans le pays. Cette liste représente l'écosystème de contenu local (gouvernement, entreprises, médias). Le statut DNSSEC de ces domaines est un excellent indicateur de la maturité en matière de sécurité des fournisseurs de contenu nationaux.

* **Requête Cypher :**
    ```cypher
    // Récupère les domaines du top 1M de Tranco résolus vers des IP hébergées dans le pays cible.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)<-[:ORIGINATE]-(:Prefix)<-[:MEMBER_OF]-(:IP)<-[:RESOLVES_TO]-(d:DomainName)
    // Utilise le classement Tranco pour filtrer par popularité
    MATCH (d)-[r:RANK]->(rk:Ranking)
    WHERE rk.name CONTAINS 'Tranco'
    RETURN d.name AS domainName,
           r.rank AS popularityRank,
           as.asn AS hostingASN
    ORDER BY r.rank ASC
    LIMIT 25;
    ```

### Objectif Global de l'Analyse

L'exécution de ces deux requêtes ne donnera pas le score d'adoption de DNSSEC, mais fournira les données essentielles pour le contextualiser et agir.

* **Compréhension :** Les deux listes de domaines (les plus *consommés* et les plus *hébergés*) constituent l'échantillon le plus pertinent pour le pays. Une fois ces listes exportées et analysées avec un outil externe (par exemple, via des scripts `dig +dnssec`), nous pourrons comprendre précisément *pourquoi* le score IRI est bon ou mauvais. Un mauvais score s'expliquerait par une absence de signature sur les domaines gouvernementaux (`.gouv.xx`), les principaux sites bancaires, les médias ou les services internationaux les plus utilisés par la population.

* **Amélioration :** Ces listes constituent un plan d'action concret. Si les domaines hébergés localement (Requête 2) ne sont pas signés, l'agence de cybersécurité nationale ou le registre du ccTLD peut lancer une campagne de sensibilisation et de formation ciblée auprès des propriétaires de ces domaines. Si les domaines internationaux populaires (Requête 1) ne sont pas signés, l'effort doit porter sur la promotion de la **validation DNSSEC** au niveau des fournisseurs d'accès Internet locaux, afin de protéger les utilisateurs même si le domaine distant n'est pas sécurisé.