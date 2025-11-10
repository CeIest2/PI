### Analyse de l’Indicateur NCI (Network Coverage Index)

Cet indicateur du pilier « Infrastructure » évalue la couverture du réseau Internet national, c’est-à-dire la présence et la distribution des opérateurs (:AS) et de leurs infrastructures sur le territoire d’un pays.
L’objectif est d’estimer la capillarité et la robustesse du maillage réseau, en combinant des mesures logiques (nombre d’AS, relations de peering) et physiques (présence de facilities ou points géographiques).

Les entités techniques clés impliquées sont :

les :AS (Systèmes Autonomes, représentant les opérateurs de réseau),

les :Facility (infrastructures physiques hébergeant ces opérateurs),

les :Point (points géographiques ou POP déclarés),

et les relations :PEERS_WITH (interconnexions entre opérateurs).

### Pertinence YPI et Plan d’Analyse Technique

Évaluation de pertinence : Cas A (Très Pertinent).
Le schéma YPI contient des données issues de PeeringDB et de CAIDA, deux sources de référence pour la topologie Internet.
Il permet de mesurer efficacement la couverture réseau à travers les AS locaux, leurs lieux d’interconnexion (:Facility, :Point) et leurs liens de peering (:PEERS_WITH).

Note sur la portée :
Le modèle ne capture pas directement la couverture de bout en bout (jusqu’aux utilisateurs finaux),
mais il décrit très fidèlement le noyau d’interconnexion nationale, composante critique de la couverture Internet structurelle.

Voici le plan d’analyse technique pour cet indicateur :

#### Requête 1 : Inventaire des AS Locaux

Objectif de la requête :
Établir le nombre total d’opérateurs de réseau enregistrés dans le pays.
Ce chiffre reflète la diversité du tissu opérateur local et constitue la base de la couverture réseau.

Requête Cypher :
```
// Couverture réseau : nombre d'AS enregistrés dans le pays.

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
RETURN c.name AS Country,
       COUNT(DISTINCT a) AS ASN_Count;
```
Interprétation :
Une valeur élevée de ASN_Count indique un marché dynamique avec une forte présence d’acteurs locaux.
Une faible valeur traduit une dépendance à quelques opérateurs dominants, ce qui peut limiter la résilience ou la concurrence.

#### Requête 2 : Couverture Physique via les Facilities

Objectif de la requête :
Évaluer la présence physique des opérateurs dans les infrastructures nationales (:Facility).
Cela renseigne sur la capacité d’interconnexion locale et la densité d’infrastructures réseau.

Requête Cypher :
```
// Couverture réseau via les infrastructures physiques (Facilities).

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:LOCATED_IN]->(f:Facility)
RETURN c.name AS Country,
       COUNT(DISTINCT f) AS InfrastructureNodes;
```
Interprétation :
Un grand nombre de InfrastructureNodes signifie une forte densité d’infrastructures locales (centres de colocation, datacenters, POP).
Si ce chiffre est faible, cela peut signaler une centralisation excessive des ressources (ex. : tout concentré à la capitale).

#### Requête 3 : Couverture Géographique Déclarée

Objectif de la requête :
Mesurer la répartition spatiale des opérateurs à travers leurs points géographiques (:Point).
Ces nœuds servent d’indicateurs de la dispersion territoriale du réseau.

Requête Cypher :
```
// Couverture réseau via les points géographiques déclarés.

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:LOCATED_IN]->(p:Point)
RETURN c.name AS Country,
       COUNT(DISTINCT p) AS GeoCoveragePoints;
```
Interprétation :
Plus le nombre de GeoCoveragePoints est élevé, plus la couverture spatiale du réseau est étendue.
Si elle est faible, cela indique que la connectivité est concentrée sur peu de zones, entraînant une couverture inégale.

#### Requête 4 : Couverture Logique via le Peering Local

Objectif de la requête :
Mesurer la densité d’interconnexion logique entre les AS d’un même pays, via les liens :PEERS_WITH.
Cela permet d’estimer la connectivité interne et la résilience du réseau national.

Requête Cypher :
```
// Mesure la couverture réseau via le peering entre AS locaux.

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:PEERS_WITH]-(b:AS)
RETURN c.name AS Country,
       COUNT(DISTINCT b) AS TotalPeerings;
```
Interprétation :
Un nombre élevé de TotalPeerings indique un réseau hautement interconnecté et performant.
À l’inverse, un faible nombre de connexions internes révèle une fragmentation du réseau national,
potentiellement dépendant de routes internationales pour le trafic local.

### Objectif Global de l’Analyse

Ces quatre requêtes offrent une vue complète de la couverture réseau nationale, en combinant :

la diversité d’opérateurs (Req 1),

la présence physique (Req 2),

la dispersion géographique (Req 3),

et la connectivité interne (Req 4).

Elles permettent d’évaluer la robustesse du maillage réseau et la maturité de l’écosystème Internet d’un pays.

### Interprétation Stratégique
Situation observée	Interprétation possible
Haute diversité d’AS + forte interconnexion	Couverture nationale solide et bien maillée
Peu d’AS + forte interconnexion	Marché concentré mais techniquement robuste
Nombreux AS + faible interconnexion	Réseau fragmenté, dépendant du transit
Peu d’AS + faible interconnexion	Écosystème sous-développé, forte dépendance internationale

### Recommandations d’Amélioration

Diversité des opérateurs (Req 1) → encourager l’entrée de nouveaux AS via régulation favorable ou politiques d’attribution d’ASN.

Infrastructure physique (Req 2) → soutenir la création de datacenters régionaux et de POP locaux.

Répartition géographique (Req 3) → promouvoir le déploiement en dehors des zones urbaines.

Connectivité locale (Req 4) → stimuler le peering national via des IXP et des forums techniques.