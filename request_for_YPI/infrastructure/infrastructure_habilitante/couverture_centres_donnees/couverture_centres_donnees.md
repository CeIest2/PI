### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Infrastructure" évalue la couverture des Points d'Échange Internet (IXP) au sein d'un pays. L'objectif est de mesurer à quel point les grands centres de population sont desservis par des IXP, ce qui est fondamental pour que le trafic Internet local reste local, améliorant ainsi la performance, la latence et la résilience du réseau national. Les entités techniques clés impliquées sont les `:IXP`, les `:AS` (en tant que membres), les `:Facility` (data centers où les IXP sont hébergés) et le `:Country`.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Très Pertinent). Le schéma YPI intègre des données complètes de PeeringDB, l'une des sources de référence pour cet indicateur IRI. YPI nous permet d'identifier les IXP d'un pays, de quantifier leur importance en comptant leurs membres et de cartographier leur empreinte physique via les data centers.

* **Note sur la portée :** Le YPI ne contient pas de données démographiques ou géospatiales sur les "grands centres de population". L'analyse se concentrera donc sur la présence, la vitalité et la distribution physique des IXP, qui sont les fondations techniques de cet indicateur de couverture.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Inventaire et Localisation des IXP du Pays

* **Objectif de la requête :** La première étape est de dresser la liste de tous les IXP présents dans le pays cible et d'identifier les villes où ils opèrent. Cela fournit un aperçu de base de l'empreinte de l'écosystème de peering national.

* **Requête Cypher :**
    ```cypher
    // Liste tous les IXP d'un pays et les villes où ils sont présents.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BR', 'DE').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(ixp:IXP)
    // Trouve les installations physiques (data centers) où l'IXP est présent.
    MATCH (ixp)-[:LOCATED_IN]->(f:Facility)
    WITH ixp, collect(DISTINCT f.city) AS cities
    // Récupère le nom officiel de l'IXP.
    OPTIONAL MATCH (ixp)-[:NAME]->(n:Name)
    RETURN n.name AS ixpName,
           ixp.id_peeringdb AS peeringdbID,
           cities
    ORDER BY ixpName;
    ```

#### Requête 2 : Mesurer la Vitalité des IXP (Nombre de Membres Locaux)

* **Objectif de la requête :** Un IXP n'est utile que si les réseaux s'y connectent. Cette requête mesure la vitalité de chaque IXP en comptant le nombre d'AS du pays qui y sont membres. Un nombre élevé de membres locaux est le signe d'un écosystème de peering sain et efficace.

* **Requête Cypher :**
    ```cypher
    // Compte le nombre de membres AS locaux pour chaque IXP dans un pays donné.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BR', 'DE').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(ixp:IXP)
    OPTIONAL MATCH (ixp)-[:NAME]->(n:Name)
    // Compte les membres (AS) de l'IXP qui sont également localisés dans le même pays.
    OPTIONAL MATCH (local_as:AS)-[:COUNTRY]->(c)
    MATCH (local_as)-[:MEMBER_OF]->(ixp)
    WITH ixp, n, count(DISTINCT local_as) as localMembersCount
    RETURN n.name as ixpName,
           localMembersCount
    ORDER BY localMembersCount DESC;
    ```

#### Requête 3 : Identifier les Principaux Acteurs Absents des IXP Locaux

* **Objectif de la requête :** Identifier les réseaux les plus importants d'un pays (en termes de taille de cône client, selon CAIDA) qui ne sont membres d'AUCUN IXP dans ce même pays. Cette information est cruciale pour identifier les "chaînons manquants" et les opportunités manquées de localisation du trafic.

* **Requête Cypher :**
    ```cypher
    // Trouve les 10 AS les plus importants d'un pays qui ne sont membres d'aucun IXP local.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BR', 'DE').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    // Utilise le classement CAIDA pour mesurer l'importance de l'AS (taille du cône client).
    MATCH (as)-[r:RANK]->(:Ranking {name:'CAIDA ASRank'})
    WHERE r.`cone:numberAsns` IS NOT NULL
    // S'assure que cet AS n'est membre d'AUCUN IXP dans le pays.
    WHERE NOT EXISTS {
      MATCH (as)-[:MEMBER_OF]->(ixp:IXP)-[:COUNTRY]->(c)
    }
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    RETURN as.asn AS asn,
           n.name AS asName,
           r.`cone:numberAsns` AS customerConeSize
    ORDER BY customerConeSize DESC
    LIMIT 10;
    ```

### Objectif Global de l'Analyse

L'exécution de ces trois requêtes fournira une image multidimensionnelle de l'écosystème de peering d'un pays, expliquant son score IRI "Couverture IXP".

* **Compréhension :** La **Requête 1** répond à la question "Avons-nous des IXP et où ?". La **Requête 2** répond à "Sont-ils utiles et activement utilisés par la communauté locale ?". La **Requête 3** révèle le potentiel inexploité en identifiant les réseaux clés qui opèrent en marge de cet écosystème. Un pays avec un mauvais score pourrait avoir un IXP (Req 1 OK), mais avec très peu de membres (Req 2 faible) et des opérateurs majeurs qui l'ignorent (Req 3 révèle des noms), ce qui signifie que sa couverture effective est quasi-nulle.

* **Amélioration :** Les résultats sont directement exploitables.
    * Si la **Requête 1** ne retourne rien, l'action prioritaire est d'amorcer la création d'un IXP national.
    * Si la **Requête 2** montre un faible nombre de membres, des actions de renforcement de la communauté sont nécessaires : organisation de forums d'opérateurs (Peering Forums), campagnes de sensibilisation sur les avantages du peering, ou subventions pour les coûts de connexion.
    * Si la **Requête 3** identifie des acteurs majeurs absents, une démarche ciblée peut être entreprise auprès de ces opérateurs pour les encourager à rejoindre les IXP locaux, ce qui aurait un impact significatif sur la localisation du trafic et la résilience globale.