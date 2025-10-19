### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Sécurité" mesure l'adhésion d'un pays aux normes MANRS (Mutually Agreed Norms for Routing Security). Un score élevé indique une forte adoption des bonnes pratiques de sécurité du routage par les opérateurs réseau du pays, visant à prévenir les incidents courants comme les détournements de routes (hijacking) et l'usurpation d'adresses IP (spoofing). Les entités techniques clés sont les `:AS` (Systèmes Autonomes) situés dans un `:Country` donné et leur relation avec l'organisation MANRS et les actions spécifiques qu'elle promeut.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Très Pertinent). Le schéma YPI intègre directement les données de MANRS, ce qui permet de vérifier l'adhésion des AS et les actions qu'ils mettent en œuvre. Nous pouvons donc directement sonder la réalité technique qui sous-tend le score de l'IRI.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Calculer le taux d'adoption de MANRS dans le pays

* **Objectif de la requête :** Cette requête fournit la statistique la plus fondamentale : le pourcentage d'opérateurs réseau (AS) dans un pays qui sont membres de l'initiative MANRS. C'est une mesure directe et quantitative de l'adoption, qui permet de contextualiser immédiatement le score IRI.

* **Requête Cypher :**
    ```cypher
    // Calcule le taux de pénétration de MANRS pour un pays donné.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    WITH count(DISTINCT as) AS totalASNsInCountry
    
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(manrsAS:AS)-[:MEMBER_OF]->(:Organization {name:"MANRS"})
    WITH totalASNsInCountry, count(DISTINCT manrsAS) AS manrsMemberCount
    
    RETURN
      totalASNsInCountry,
      manrsMemberCount,
      // Calcule le pourcentage d'adoption.
      round(100.0 * manrsMemberCount / totalASNsInCountry, 2) AS adoptionRatePercentage;
    ```

#### Requête 2 : Identifier les membres MANRS les plus influents

* **Objectif de la requête :** Au-delà du simple nombre, il est crucial de savoir si les réseaux les plus importants (ceux avec le plus grand nombre de clients) sont membres. L'adhésion d'un grand fournisseur de transit ou d'un FAI majeur a un impact disproportionné sur la résilience du pays. Cette requête liste les membres MANRS du pays et les classe par la taille de leur cône de clients (selon le classement CAIDA AS Rank) pour identifier les piliers de la sécurité du routage local.

* **Requête Cypher :**
    ```cypher
    // Liste les membres MANRS d'un pays et leur importance (taille du cône client).
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)-[:MEMBER_OF]->(:Organization {name:"MANRS"})
    
    // Jointure optionnelle avec le classement CAIDA pour obtenir la taille du cône client.
    OPTIONAL MATCH (as)-[r:RANK]->(:Ranking {name:'CAIDA ASRank'})
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    
    RETURN
      as.asn AS asn,
      n.name AS asName,
      r['cone:numberAsns'] AS customerConeSize
    ORDER BY customerConeSize DESC
    LIMIT 20;
    ```

#### Requête 3 : Vérifier la mise en œuvre des actions MANRS

* **Objectif de la requête :** L'adhésion à MANRS est une déclaration d'intention ; la mise en œuvre d'actions concrètes est la preuve de l'engagement. Cette requête vérifie quelles actions spécifiques (filtrage, anti-spoofing, etc.) ont été implémentées par les membres MANRS du pays. Cela permet de différencier les membres actifs des membres passifs et d'évaluer la maturité de l'écosystème.

* **Requête Cypher :**
    ```cypher
    // Dresse l'inventaire des actions MANRS implémentées par les membres dans un pays.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)-[:MEMBER_OF]->(:Organization {name:"MANRS"})
    MATCH (as)-[:IMPLEMENT]->(action:ManrsAction)
    
    WITH action, count(DISTINCT as) AS implementingASNs
    
    RETURN
      action.label AS manrsAction,
      implementingASNs
    ORDER BY implementingASNs DESC;
    ```

### Objectif Global de l'Analyse

L'exécution de ces trois requêtes fournira une vue d'ensemble détaillée de la posture de sécurité du routage d'un pays, bien au-delà d'un simple score.

* **Compréhension :** La **Requête 1** donne le chiffre brut d'adoption. Si ce chiffre est bas, cela explique immédiatement un mauvais score IRI. La **Requête 2** affine cette analyse : même si le taux global est moyen, si les AS avec les plus grands `customerConeSize` sont tous membres, la résilience réelle peut être meilleure que ne le suggère le score. Inversement, un bon score peut cacher le fait qu'un opérateur national critique n'est pas membre, ce qui représente un risque important. Enfin, la **Requête 3** mesure l'engagement réel. Un pays avec de nombreux membres mais peu d'actions implémentées a un problème de maturité, pas seulement d'adoption.

* **Amélioration :** Les résultats sont directement exploitables.
    * Un faible taux d'adoption (Requête 1) suggère la nécessité d'une campagne de sensibilisation nationale auprès de la communauté des opérateurs (via le NOG local, par exemple).
    * Si des AS critiques ne sont pas membres (Requête 2), une action de plaidoyer ciblée auprès de ces acteurs spécifiques est la stratégie la plus efficace.
    * Si une action clé (comme l'anti-spoofing) est rarement implémentée (Requête 3), cela indique un besoin de formation technique, de guides de bonnes pratiques ou d'ateliers pour aider les opérateurs à surmonter les obstacles techniques à sa mise en œuvre.