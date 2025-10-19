### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Sécurité" évalue la capacité d'un pays à résister aux attaques par déni de service distribué (DDoS). Un bon score signifie que les infrastructures et services critiques du pays disposent de mécanismes de protection pour absorber ou filtrer le trafic malveillant, garantissant ainsi la continuité du service lors d'une attaque. Les entités techniques clés sont les **Systèmes Autonomes (`:AS`)** qui peuvent être à la fois des cibles et des vecteurs de protection, et plus spécifiquement les réseaux de diffusion de contenu (**CDN - Content Delivery Networks**) qui constituent une première ligne de défense majeure contre les attaques DDoS à grande échelle.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Pertinent, via une analyse par proxy). Le schéma YPI ne contient pas de propriété explicite "protection_ddos: true". Cependant, il est possible d'évaluer cet indicateur de manière très efficace en utilisant les **CDN comme proxy**. La présence, la portée et l'utilisation d'infrastructures CDN dans un pays sont des indicateurs techniques forts de sa résilience face aux DDoS. Un écosystème CDN robuste signifie qu'une part importante du trafic est distribuée et protégée par défaut.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Identifier les CDN avec une présence locale

* **Objectif de la requête :** La première étape consiste à dresser l'inventaire des réseaux CDN qui opèrent directement dans le pays. La présence physique de ces réseaux (via un AS enregistré dans le pays) est un signe de résilience, car elle permet une mitigation plus proche de la source et des utilisateurs, réduisant la latence et la dépendance aux liens internationaux.

* **Requête Cypher :**
    ```cypher
    // Liste les AS catégorisés comme CDN et localisés dans un pays spécifique.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    // Utilise les étiquettes de bgp.tools pour identifier les CDN.
    MATCH (as)-[:CATEGORIZED]->(t:Tag {label: 'CDN'})
    // Récupère le nom de l'AS pour une meilleure lisibilité.
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    RETURN as.asn AS cdnASN,
           n.name AS cdnName
    ORDER BY cdnName;
    ```

#### Requête 2 : Évaluer la portée des CDN auprès de la population

* **Objectif de la requête :** Savoir qu'un CDN est présent ne suffit pas ; il faut mesurer son importance. Cette requête utilise les données de population d'APNIC pour estimer quel pourcentage des internautes d'un pays est desservi par chaque CDN local. Un CDN couvrant une grande partie de la population offre une couche de protection à grande échelle.

* **Requête Cypher :**
    ```cypher
    // Mesure le pourcentage de la population d'un pays desservi par des AS de type CDN.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
    MATCH (as)-[:CATEGORIZED]->(t:Tag {label: 'CDN'})
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    RETURN as.asn AS cdnASN,
           n.name AS cdnName,
           p.percent AS populationServedPercentage
    ORDER BY populationServedPercentage DESC;
    ```

#### Requête 3 : Vérifier la protection des domaines populaires

* **Objectif de la requête :** Cette requête vérifie si les services en ligne les plus populaires auprès des citoyens du pays (selon Cloudflare Radar) sont effectivement protégés par des infrastructures CDN (locales ou internationales). Cela permet de passer de la disponibilité de l'infrastructure à son utilisation effective pour protéger les services critiques ou à fort trafic.

* **Requête Cypher :**
    ```cypher
    // Identifie les domaines populaires dans un pays et vérifie s'ils sont hébergés par un CDN.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'DE', 'BR').
    // Trouve les domaines les plus interrogés depuis le pays.
    MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)
    WITH d, q.value AS queryPercentage ORDER BY queryPercentage DESC LIMIT 20
    // Trouve l'AS qui annonce l'IP de ces domaines.
    MATCH (d)-[:RESOLVES_TO]->(:IP)-[:ORIGINATE]->(hostAS:AS)
    // Vérifie si cet AS est un CDN.
    WHERE (hostAS)-[:CATEGORIZED]->(:Tag {label:"CDN"})
    OPTIONAL MATCH (hostAS)-[:NAME]->(n:Name)
    RETURN d.name AS popularDomain,
           hostAS.asn AS hostingCdnASN,
           n.name AS hostingCdnName,
           queryPercentage
    ORDER BY queryPercentage DESC;
    ```

### Objectif Global de l'Analyse

* **Compréhension :** L'ensemble de ces requêtes fournit une vue multi-facettes de la résilience DDoS d'un pays. Un mauvais score à l'indicateur IRI "Protection DDoS" pourrait s'expliquer par :
    1.  Une absence ou un très faible nombre de CDN opérant localement (résultat faible à la **Requête 1**).
    2.  Les CDN présents ne desservent qu'une petite fraction de la population, laissant la majorité exposée (résultat faible à la **Requête 2**).
    3.  Les sites et services les plus importants du pays ne tirent pas parti des solutions CDN et sont hébergés sur des infrastructures vulnérables (résultat faible à la **Requête 3**).
    Inversement, de bons résultats à ces trois requêtes montreraient un écosystème mature où l'infrastructure de mitigation est non seulement présente et étendue, mais aussi activement utilisée pour protéger les services essentiels.

* **Amélioration :** Les résultats de cette analyse pointent vers des actions concrètes. Si la présence de CDN est faible, une politique nationale visant à attirer les grands acteurs CDN pour qu'ils installent des points de présence (PoP) dans des centres de données (`:Facility`) locaux serait une priorité. Si les domaines populaires ne sont pas protégés, il faudrait lancer des programmes de sensibilisation et d'incitation auprès des fournisseurs de contenu locaux, des entreprises et des agences gouvernementales pour les encourager à adopter des solutions CDN, renforçant ainsi la sécurité de l'écosystème numérique national dans son ensemble.