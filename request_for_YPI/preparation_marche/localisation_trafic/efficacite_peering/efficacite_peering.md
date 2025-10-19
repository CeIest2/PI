### Analyse de l'Indicateur IRI

Cet indicateur du pilier "Préparation du Marché" mesure l'adoption du peering local au sein d'un pays. Il calcule le ratio entre le nombre de réseaux (AS) qui sont membres d'au moins un Point d'Échange Internet (IXP) local, et le nombre total de réseaux dans ce pays. Un score élevé indique un écosystème d'interconnexion mature où le trafic local reste local, ce qui améliore la résilience, réduit la latence et diminue les coûts de transit. Les entités techniques clés sont les `:AS` et les `:IXP` situés dans le pays, ainsi que la relation qui les lie.

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Très Pertinent). Le schéma YPI, grâce à l'intégration des données de PeeringDB, est parfaitement adapté pour cette analyse. Il contient les nœuds `:AS` et `:IXP`, leur localisation géographique via la relation `[:COUNTRY]`, et la relation cruciale `[:MEMBER_OF]` qui connecte un AS à un IXP.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Dénombrement des AS Membres d'un IXP Local

* **Objectif de la requête :** Calculer le numérateur du ratio de l'IRI. Cette requête identifie et compte le nombre unique de réseaux (AS) d'un pays qui sont explicitement listés comme membres d'au moins un IXP situé dans ce même pays. C'est la mesure directe de la participation à l'écosystème de peering local.

* **Requête Cypher :**
    ```cypher
    // Calcule le nombre d'AS locaux membres d'un IXP local.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'NG', 'US').
    MATCH (c:Country {country_code: $countryCode})
    // Trouve les IXP dans le pays cible.
    MATCH (ixp:IXP)-[:COUNTRY]->(c)
    // Trouve les AS dans ce même pays qui sont membres de ces IXP.
    MATCH (as:AS)-[:COUNTRY]->(c)
    MATCH (as)-[:MEMBER_OF]->(ixp)
    RETURN count(DISTINCT as.asn) AS numberOfPeeringASNs;
    ```

#### Requête 2 : Calculer le Ratio d'Efficacité du Peering

* **Objectif de la requête :** Reconstruire le score de l'indicateur IRI en calculant le ratio. Cette requête calcule d'abord le nombre total d'AS dans le pays (le dénominateur), puis le nombre d'AS qui peer localement (le numérateur, via un sous-requête), et enfin retourne le ratio d'efficacité. Cela permet de valider et de comprendre la valeur numérique de l'indicateur.

* **Requête Cypher :**
    ```cypher
    // Calcule le ratio des AS locaux qui peerent sur un IXP local.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'NG', 'US').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    WITH count(DISTINCT as) AS totalASNs, c
    
    // Sous-requête pour compter les AS qui peerent localement.
    CALL {
        WITH c
        MATCH (ixp:IXP)-[:COUNTRY]->(c)
        MATCH (local_as:AS)-[:COUNTRY]->(c)
        MATCH (local_as)-[:MEMBER_OF]->(ixp)
        RETURN count(DISTINCT local_as) AS peeringASNs
    }
    
    RETURN totalASNs,
           peeringASNs,
           // Calcule et formate le ratio en pourcentage.
           round(100.0 * peeringASNs / totalASNs, 2) AS peeringEfficiencyRatio;
    ```

#### Requête 3 : Identifier les Principaux Réseaux "Non-Peerers"

* **Objectif de la requête :** Aller au-delà du simple score pour identifier des cibles d'action. Cette requête liste les réseaux les plus significatifs du pays (en termes de taille de cône client, selon CAIDA) qui ne sont membres d'aucun IXP local. Identifier ces "chaînons manquants" est crucial pour comprendre *pourquoi* le score est ce qu'il est, et qui contacter pour l'améliorer.

* **Requête Cypher :**
    ```cypher
    // Identifie les AS locaux les plus importants qui ne peerent sur aucun IXP local.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'NG', 'US').
    MATCH (c:Country {country_code: $countryCode})
    
    // Créer une liste de tous les AS qui peerent localement.
    MATCH (ixp:IXP)-[:COUNTRY]->(c)
    MATCH (peeringAS:AS)-[:MEMBER_OF]->(ixp)
    WHERE (peeringAS)-[:COUNTRY]->(c)
    WITH c, collect(DISTINCT peeringAS) AS peerers
    
    // Trouver tous les AS dans le pays qui NE SONT PAS dans la liste des peerers.
    MATCH (nonPeerer:AS)-[:COUNTRY]->(c)
    WHERE not nonPeerer IN peerers
    
    // Récupérer leur rang et nom pour le contexte.
    OPTIONAL MATCH (nonPeerer)-[r:RANK]->(:Ranking {name:'CAIDA ASRank'})
    OPTIONAL MATCH (nonPeerer)-[:NAME]->(n:Name)
    
    RETURN nonPeerer.asn AS nonPeererASN,
           n.name AS nonPeererName,
           r['cone:numberAsns'] AS customerConeSize
    ORDER BY customerConeSize DESC
    LIMIT 15;
    ```

### Objectif Global de l'Analyse

L'exécution de cet ensemble de requêtes fournira une image complète de l'écosystème de peering d'un pays.

* **Compréhension :** La **Requête 2** nous donnera le chiffre brut qui sous-tend le score de l'IRI. Si ce ratio est faible, la **Requête 3** nous en expliquera la raison fondamentale : elle identifiera nommément les réseaux qui manquent à l'appel. Si les réseaux en tête de cette liste sont de grands opérateurs mobiles, des fournisseurs d'accès gouvernementaux ou des universités importantes, nous saurons que l'absence de quelques acteurs clés pénalise l'ensemble de l'écosystème national.

* **Amélioration :** Les résultats sont directement exploitables. La liste générée par la **Requête 3** constitue une feuille de route pour des actions de plaidoyer ciblées. Au lieu d'une campagne générale, l'ISOC peut engager des discussions directes avec les dirigeants de ces réseaux "non-peerers" identifiés, en leur présentant les avantages techniques et économiques du peering local. Encourager un seul grand réseau de cette liste à rejoindre un IXP peut avoir un impact disproportionné sur le score d'efficacité du peering et, plus important encore, sur la résilience réelle de l'Internet dans le pays.