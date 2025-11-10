### Analyse de l'Indicateur IRI

Cet indicateur, situé dans le pilier "Sécurité" et le sous-pilier "Hygiène du routage", vise à évaluer la robustesse des connexions d'un pays au reste d'Internet. Il mesure la manière et la qualité avec laquelle les réseaux (Systèmes Autonomes - AS) d'un pays sont connectés à leurs fournisseurs de transit Internet, aussi appelés fournisseurs "amont" (upstream). Un bon score suggère que les réseaux locaux disposent de connexions nombreuses et de haute qualité vers le reste d'Internet, ce qui réduit les risques d'isolement en cas de panne d'un fournisseur majeur. Les entités techniques clés sont les `:AS` du pays cible, les `:AS` agissant comme leurs fournisseurs, et les relations qui les unissent.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Très Pertinent). Le schéma YPI est idéal pour cette analyse. Il contient non seulement les relations de transit (fournisseur-à-client) via BGPKIT, mais aussi les données de classement de CAIDA (AS Rank), qui sont la source de référence pour cet indicateur IRI. Nous pouvons donc à la fois identifier les connexions et évaluer leur qualité.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Identifier les Fournisseurs Amont et Évaluer leur Qualité

* **Objectif de la requête :** Cette requête dresse un inventaire complet des fournisseurs de transit pour un pays donné. Pour chaque fournisseur, elle compte le nombre de réseaux clients locaux qu'il dessert et, surtout, elle récupère son classement mondial selon CAIDA (AS Rank). Un rang faible (proche de 1) indique un fournisseur majeur au cœur de l'Internet. Cette requête permet de visualiser à la fois la quantité et la qualité intrinsèque des connexions amont du pays.

* **Requête Cypher :**
    ```cypher
    // Identifie les fournisseurs de transit d'un pays, compte leurs clients locaux et affiche leur rang CAIDA.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'NG', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(local_as:AS)
    // Trouve la relation fournisseur-à-client (rel=1) via les données BGPKIT.
    MATCH (local_as)-[:PEERS_WITH {rel: 1}]->(provider:AS)
    // S'assure que le fournisseur est externe au pays.
    WHERE NOT (provider)-[:COUNTRY]->(c)
    // Récupère le classement CAIDA du fournisseur.
    WITH provider, count(DISTINCT local_as) AS local_clients
    OPTIONAL MATCH (provider)-[r:RANK]->(rank_node:Ranking {name: 'CAIDA ASRank'})
    OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
    RETURN provider.asn AS providerASN,
           n.name AS providerName,
           local_clients,
           r.rank AS caidaASRank
    ORDER BY caidaASRank ASC, local_clients DESC
    LIMIT 20;
    ```

#### Requête 2 : Analyser la Distribution Qualitative du Portefeuille de Transit

* **Objectif de la requête :** Plutôt que de simplement lister les fournisseurs, cette requête analyse le portefeuille de transit du pays en agrégeant les fournisseurs par "tiers" de qualité, basés sur leur rang CAIDA. Elle répond à la question : "Le pays est-il principalement connecté à l'élite mondiale (Top 100), à de grands opérateurs internationaux (Top 500), ou à des acteurs plus régionaux ?". Une forte concentration dans les tiers supérieurs est un signe de grande résilience.

* **Requête Cypher :**
    ```cypher
    // Analyse la répartition des fournisseurs de transit d'un pays par catégorie de rang CAIDA.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'NG', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(local_as:AS)
    MATCH (local_as)-[:PEERS_WITH {rel: 1}]->(provider:AS)
    WHERE NOT (provider)-[:COUNTRY]->(c)
    // Récupère le classement CAIDA de chaque fournisseur unique.
    WITH DISTINCT provider
    MATCH (provider)-[r:RANK]->(rank_node:Ranking {name: 'CAIDA ASRank'})
    // Catégorise chaque fournisseur en fonction de son rang.
    WITH provider, r.rank AS rank
    WITH CASE
        WHEN rank <= 100 THEN 'A) Top 100 (Coeur Internet)'
        WHEN rank > 100 AND rank <= 500 THEN 'B) Top 101-500 (Majeur)'
        WHEN rank > 500 AND rank <= 2000 THEN 'C) Top 501-2000 (Important)'
        ELSE 'D) Au-delà de 2000 (Régional/Niche)'
    END AS providerTier
    // Compte le nombre de fournisseurs dans chaque catégorie.
    RETURN providerTier,
           count(provider) AS numberOfProviders
    ORDER BY providerTier ASC;
    ```

### Requête 3 : Concentration des Fournisseurs en Amont

* **Objectif de la requête :** Cette requête identifie les principaux points de concentration du peering externe. Elle recherche les AS étrangers (peers) qui sont connectés au plus grand nombre d'AS domestiques. Un nombre élevé de clients pour un seul peer externe peut indiquer une forte dépendance.

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

---

### Requête 4 : Diversité des Peers en Amont

* **Objectif de la requête :** Cette requête évalue la diversité globale des connexions externes. Elle compte le nombre total d'AS domestiques et le compare au nombre total de peers externes uniques auxquels ils sont connectés. Un ratio élevé de peers par opérateur domestique suggère une connectivité riche et diversifiée.

* **Requête Cypher :**
    ```cypher
    // 1. Diversité des peers en amont
    
    // 1. Trouver le pays et ses AS
    MATCH (c:Country {country_code: countryCode})
    MATCH (c)<-[:COUNTRY]-(as_fr:AS)
    
    // 2. Trouver tous les peers de ces AS
    MATCH (as_fr)-[:PEERS_WITH]-(peer:AS)
    
    // 3. Trouver le pays de ces peers
    MATCH (peer)-[:COUNTRY]->(peer_country:Country)
    
    // 4. Filtrer pour ne garder que les peers EXTERNES
    WHERE peer_country <> c
    
    // 5. Compter les AS domestiques et les peers externes uniques
    RETURN c.name AS pays,
           count(DISTINCT as_fr) AS operateursDomestiques,
           count(DISTINCT peer) AS peersExternesUniques
    ORDER BY peersExternesUniques DESC
    ```

---

### Requête 5 : Présence dans les IXP Internationaux

* **Objectif de la requête :** Cette requête mesure l'implication des opérateurs d'un pays dans les points d'échange Internet (IXP) situés à l'étranger. Se connecter à des IXP internationaux est une stratégie clé pour diversifier la connectivité, réduire les coûts de transit et améliorer la latence vers des réseaux étrangers.

* **Requête Cypher :**
    ```cypher
    // 3. Présence dans les IXP internationaux
    
    // 1. Trouver le pays et ses AS
    MATCH (c:Country {country_code: countryCode})
    MATCH (c)<-[:COUNTRY]-(as_fr:AS)
    
    // 2. Trouver les IXP dont ils sont membres
    MATCH (as_fr)-[:MEMBER_OF]->(ixp:IXP)
    
    // 3. Trouver le pays de l'IXP
    MATCH (ixp)-[:COUNTRY]->(ixp_country:Country)
    
    // 4. Filtrer pour ne garder que les IXP à l'étranger
    WHERE ixp_country <> c
    
    // 5. Compter
    RETURN c.name AS pays,
           count(DISTINCT ixp) AS ixpInternationauxUniques,
           count(DISTINCT as_fr) AS operateursConnectesInternational
    ORDER BY operateursConnectesInternational DESC
    ```

### Objectif Global de l'Analyse

L'exécution de ces requêtes fournira une image claire et détaillée de la connectivité amont du pays, expliquant directement son score IRI sur cet indicateur.

* **Compréhension :** Si le score IRI du pays est bon, nous nous attendons à ce que la **Requête 1** retourne une liste variée de fournisseurs avec des rangs CAIDA très bas (beaucoup d'AS dans le top 100). La **Requête 2** confirmera cela en montrant un nombre élevé de fournisseurs dans la catégorie "A) Top 100". Inversement, un mauvais score se traduira par une liste courte dans la Requête 1, potentiellement dominée par des fournisseurs au rang CAIDA élevé, et la Requête 2 montrera une concentration de fournisseurs dans les catégories "C)" ou "D)", indiquant une dépendance à des acteurs de second ou troisième plan.

* **Amélioration :** Les résultats sont directement exploitables. Si l'analyse révèle une faible connectivité aux fournisseurs du cœur d'Internet (peu ou pas de fournisseurs dans la catégorie "A"), une action stratégique serait de développer des politiques publiques pour attirer les grands opérateurs de transit mondiaux à établir un point de présence (PoP) dans le pays. Cela pourrait passer par la création de data centers "carrier-neutral" ou des incitations fiscales, afin de faciliter pour les AS locaux l'établissement de connexions directes, plus performantes et plus résilientes, avec le cœur de l'Internet mondial.