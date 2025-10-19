### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Sécurité" mesure le niveau de déploiement et d'utilisation du protocole Internet de nouvelle génération, IPv6, au sein d'un pays. Une forte adoption d'IPv6 est un signe de modernisation de l'infrastructure réseau, essentielle pour la croissance future d'Internet et pour surmonter la pénurie d'adresses IPv4. Les entités techniques clés sont les `:AS` (opérateurs réseau) et les `:Prefix` (blocs d'adresses IP), en distinguant spécifiquement les préfixes IPv6.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Très Pertinent). Le schéma YPI intègre des données de routage BGP (via BGPKIT, PCH, etc.) qui permettent d'identifier précisément quels systèmes autonomes (`:AS`) annoncent des préfixes IPv6, offrant ainsi une mesure directe de l'adoption côté infrastructure.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Taux d'adoption d'IPv6 par les opérateurs (AS)

* **Objectif de la requête :** Obtenir une vue d'ensemble quantitative. Cette requête calcule le pourcentage de systèmes autonomes (AS) dans un pays donné qui annoncent activement au moins un préfixe IPv6. C'est la mesure de base de la "préparation IPv6" des opérateurs du pays.

* **Requête Cypher :**
    ```cypher
    // Calcule le pourcentage d'AS dans un pays qui annoncent des préfixes IPv6.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    WITH count(DISTINCT as) AS totalASNs, c

    MATCH (c)<-[:COUNTRY]-(as_v6:AS)-[:ORIGINATE]->(p:Prefix)
    WHERE p.prefix CONTAINS ':'
    WITH totalASNs, count(DISTINCT as_v6) AS ipv6EnabledASNs

    RETURN
        totalASNs,
        ipv6EnabledASNs,
        // Calcule le ratio en pourcentage.
        round(100.0 * ipv6EnabledASNs / totalASNs, 2) AS adoptionRatePercentage;
    ```

#### Requête 2 : Identifier les réseaux clés (par taille de cône client) n'ayant pas adopté IPv6

* **Objectif de la requête :** Aller au-delà du simple pourcentage pour identifier les "retardataires" les plus influents. Un grand opérateur de transit sans IPv6 a un impact beaucoup plus important qu'un petit. Cette requête liste les AS du pays qui n'annoncent aucun préfixe IPv6, classés par leur importance (taille du cône client selon CAIDA), afin de prioriser les efforts de sensibilisation.

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

#### Requête 3 : Disponibilité d'IPv6 pour le contenu local populaire

* **Objectif de la requête :** Évaluer l'adoption du point de vue de l'utilisateur final. Même si les opérateurs sont prêts, l'expérience IPv6 est limitée si les contenus et services les plus consultés ne sont pas accessibles via ce protocole. Cette requête vérifie, pour les domaines les plus populaires dans le pays (selon Cloudflare Radar), s'ils disposent d'adresses IPv6 (enregistrement AAAA).

* **Requête Cypher :**
    ```cypher
    // Vérifie la disponibilité IPv6 des domaines les plus populaires d'un pays.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
    MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)

    // Ordonne par popularité et prend le top 20.
    WITH d, q.value AS popularity ORDER BY popularity DESC LIMIT 20
    
    // Récupère toutes les adresses IP associées au domaine.
    MATCH (d)-[:RESOLVES_TO]->(ip:IP)
    WITH d, popularity, collect(ip.address) AS ipAddresses

    RETURN
        d.name AS domain,
        // Vérifie si AU MOINS UNE des adresses IP est une adresse IPv6.
        ANY(addr IN ipAddresses WHERE addr CONTAINS ':') AS isIPv6Enabled
    ORDER BY popularity DESC;
    ```

### Objectif Global de l'Analyse

L'exécution combinée de ces trois requêtes fournit une analyse complète et exploitable de l'adoption d'IPv6, bien au-delà d'un simple score.

* **Compréhension :** La **Requête 1** donne le chiffre global de la préparation des infrastructures. Si ce chiffre est bas, nous savons que le problème est fondamental. La **Requête 2** nous dit précisément *qui* sont les acteurs bloquants ; si les AS en tête de cette liste sont des opérateurs majeurs, nous comprenons pourquoi le score national est faible. Enfin, la **Requête 3** déplace la perspective vers le contenu ; un bon score aux deux premières requêtes mais un mauvais à la troisième indiquerait que l'infrastructure est prête, mais que l'écosystème de contenu local n'a pas suivi, limitant les bénéfices pour l'utilisateur final.

* **Amélioration :** Les résultats sont directement exploitables. La liste générée par la **Requête 2** devient une feuille de route pour des actions de plaidoyer et de renforcement des capacités ciblées vers les opérateurs les plus influents. La liste de la **Requête 3** permet d'engager le dialogue avec les principaux fournisseurs de contenu locaux (gouvernement, médias, banques) pour les encourager à activer IPv6 sur leurs services, créant ainsi un cercle vertueux d'adoption.