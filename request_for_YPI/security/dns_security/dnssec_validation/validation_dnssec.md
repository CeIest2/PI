### Analyse de l'Indicateur IRI : Validation DNSSEC

Cet indicateur du pilier "Sécurité" évalue dans quelle mesure les résolveurs DNS d'un pays effectuent une validation DNSSEC. Il ne s'agit pas de savoir si les domaines sont signés (ce qui correspond à l'indicateur "Adoption de DNSSEC"), mais si les systèmes côté client (généralement les résolveurs des fournisseurs d'accès) vérifient ces signatures pour protéger les utilisateurs finaux contre les réponses DNS falsifiées (ex: empoisonnement du cache DNS). Les entités techniques clés sont les **résolveurs DNS**, qui sont opérés au sein des **Autonomous Systems (`:AS`)**, en particulier ceux qui fournissent un accès direct aux utilisateurs ("eyeball networks").

### Pertinence YPI et Plan d'Analyse Technique

* **Évaluation de pertinence :** Cas A (Pertinent, via des proxys). Le schéma YPI ne contient pas de données directes mesurant si un résolveur DNS spécifique effectue la validation. Cependant, nous pouvons utiliser un proxy puissant : l'adhésion des opérateurs réseau aux meilleures pratiques de sécurité, notamment via l'initiative **MANRS**. Un opérateur qui s'engage publiquement dans la sécurité du routage (MANRS) est beaucoup plus susceptible d'avoir également mis en œuvre des protections DNS comme la validation DNSSEC. L'analyse se concentrera donc sur la maturité sécuritaire des opérateurs du pays.

Voici le plan d'analyse technique pour cet indicateur :

#### Requête 1 : Taux d'adoption de MANRS dans le pays

* **Objectif de la requête :** Calculer le pourcentage d'opérateurs réseau (AS) dans le pays qui sont membres de MANRS. Ce chiffre global donne une première mesure de la maturité et de l'engagement de l'écosystème local en matière de sécurité Internet, ce qui est un prérequis culturel et technique pour une bonne validation DNSSEC.

* **Requête Cypher :**
    ```cypher
    // Calcule le pourcentage d'AS membres de MANRS dans un pays donné.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})
    // Compte le nombre total d'AS dans le pays.
    OPTIONAL MATCH (as:AS)-[:COUNTRY]->(c)
    WITH c, count(DISTINCT as) AS totalASNs
    // Compte le nombre d'AS membres de MANRS dans ce même pays.
    OPTIONAL MATCH (manrs_as:AS)-[:COUNTRY]->(c)
    WHERE (manrs_as)-[:MEMBER_OF]->(:Organization {name:"MANRS"})
    WITH totalASNs, count(DISTINCT manrs_as) AS manrsASNs
    RETURN
        manrsASNs,
        totalASNs,
        CASE
            WHEN totalASNs > 0 THEN (toFloat(manrsASNs) / totalASNs) * 100
            ELSE 0
        END AS manrsAdoptionPercentage;
    ```

#### Requête 2 : Vérifier le statut MANRS des principaux réseaux d'accès ("eyeball networks")

* **Objectif de la requête :** La validation DNSSEC a le plus d'impact lorsqu'elle est effectuée par les fournisseurs d'accès Internet (FAI) qui servent la majorité de la population. Cette requête identifie les réseaux les plus importants du pays en termes de population desservie (selon les estimations d'APNIC) et vérifie spécifiquement leur statut MANRS. Si les principaux FAI ne sont pas membres, la protection pour la majorité des utilisateurs est probablement faible.

* **Requête Cypher :**
    ```cypher
    // Identifie les plus grands réseaux d'accès (par population) et vérifie leur adhésion à MANRS.
    // Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})<-[pop:POPULATION]-(as:AS)
    // Récupère le nom de l'AS.
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    // Vérifie si l'AS est membre de MANRS.
    OPTIONAL MATCH (as)-[:MEMBER_OF]->(m:Organization {name:"MANRS"})
    RETURN
        as.asn AS asn,
        n.name AS name,
        pop.percent AS populationServedPercentage,
        (m IS NOT NULL) AS isManrsMember
    ORDER BY populationServedPercentage DESC
    LIMIT 10;
    ```

### Objectif Global de l'Analyse

L'exécution de ces requêtes fournira une évaluation factuelle de la posture de sécurité de l'écosystème réseau du pays, servant de proxy pour la validation DNSSEC.

* **Compréhension :** Si le score IRI pour la validation DNSSEC est faible, ces requêtes aideront à en comprendre la raison technique. Un faible `manrsAdoptionPercentage` (Requête 1) et, plus important encore, un `isManrsMember = false` pour les principaux réseaux d'accès (Requête 2) démontreront que les opérateurs les plus critiques pour la sécurité des utilisateurs finaux n'ont pas encore adopté les meilleures pratiques fondamentales. Cela explique pourquoi la validation DNSSEC, une pratique plus avancée, est probablement négligée.

* **Amélioration :** Les résultats de ces requêtes sont directement exploitables. Si l'analyse révèle que des FAI majeurs ne sont pas membres de MANRS, une action ciblée peut être menée. L'Internet Society peut engager directement ces opérateurs, en utilisant les données de la Requête 2, pour promouvoir les avantages de MANRS, offrir une assistance technique et organiser des ateliers de formation. En augmentant l'adoption de MANRS, on renforce la culture et les compétences en matière de sécurité, ce qui crée un terrain fertile pour encourager et mettre en œuvre la validation DNSSEC à l'échelle nationale.