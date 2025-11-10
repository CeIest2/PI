### Analyse de l’Indicateur FRI (Fibre Reach Index)

Cet indicateur du pilier « Infrastructure » évalue la portée du réseau fibre au sein d’un pays.
L’objectif est de mesurer la densité et la proximité des infrastructures de connectivité qui permettent aux services haut débit (fibre, backbone IP) d’atteindre efficacement les zones desservies.
Plus la distribution des points de présence et des interconnexions locales est dense, plus la portée du réseau fibre est grande — c’est-à-dire que la fibre est disponible à faible distance des opérateurs et potentiellement des utilisateurs.

Les entités techniques clés impliquées sont :

les :AS (systèmes autonomes, équivalents des opérateurs de réseau),

les :Point (points géographiques ou nœuds physiques du réseau),

les relations :LOCATED_IN (localisation des AS dans ces points),

et les relations :PEERS_WITH (liens d’interconnexion directe entre opérateurs).

Pertinence YPI et Plan d’Analyse Technique

Évaluation de pertinence : Cas B (Pertinent mais partiel).
Le schéma YPI (Your Peering Intelligence) ne contient pas de métriques physiques sur les fibres (longueurs, topologie ou débits),
mais il offre un proxy robuste via les points réseau (:Point) et les relations de peering (:PEERS_WITH).
Ces éléments permettent une approximation réaliste de la portée de la fibre à travers la densité et la connectivité locale des AS.

Note sur la portée :
Le modèle YPI ne permet pas de mesurer la distance réelle de 10 km ni la couverture client,
mais il capture bien la structure du maillage de connectivité, essentielle pour estimer la proximité réseau effective.

Voici le plan d’analyse technique pour cet indicateur :

Requête 1 : Densité de Points Réseau Locaux

Objectif de la requête :
Évaluer la densité des points géographiques où sont présents les AS d’un pays.
Plus il y a de :Point uniques associés à des :AS locaux, plus le maillage est dense,
et plus la portée de la fibre est étendue sur le territoire.

Requête Cypher :
```
// Approximation de la portée fibre : densité de points géographiques des AS
// $countryCode = code du pays (ex: 'FR', 'SN', 'JP')

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:LOCATED_IN]->(p:Point)
RETURN c.name AS Country,
       COUNT(DISTINCT p) AS GeoCoveragePoints,
       COUNT(DISTINCT a) AS Operators
ORDER BY GeoCoveragePoints DESC;
```
Interprétation des résultats :
Un nombre élevé de GeoCoveragePoints indique une bonne répartition des infrastructures et une grande proximité locale.
Si la valeur est faible, cela suggère une concentration des opérateurs dans peu de zones, traduisant une portée fibre limitée.

Requête 2 : Proximité Réseau Locale (Peering)

Objectif de la requête :
Mesurer la proximité fonctionnelle entre les opérateurs d’un pays via les connexions :PEERS_WITH.
Dans ce modèle, un AS ayant de nombreux voisins locaux est fortement interconnecté,
ce qui traduit une portée réseau courte et une connectivité fibre efficace (faible distance logique entre réseaux).

Requête Cypher :
```
// Approxime la proximité fibre : nombre de voisins réseau locaux.
// Plus un AS a de connexions PEERS_WITH, plus il a une "portée" courte.

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:PEERS_WITH]-(b:AS)
RETURN a.asn AS ASN,
       COUNT(DISTINCT b) AS LocalNeighbors
ORDER BY LocalNeighbors DESC
LIMIT 20;
```
Interprétation des résultats :
Les AS en tête de cette liste sont les nœuds les plus interconnectés du pays,
souvent les opérateurs d’infrastructure ou les points de concentration régionaux (backbones, grands FAI).
Si peu d’AS possèdent un grand nombre de voisins, cela indique une structure centralisée — bonne pour la performance urbaine, mais moins favorable à la couverture nationale.
Si la connectivité est distribuée, cela montre une portée fibre équilibrée sur plusieurs opérateurs.

Objectif Global de l’Analyse

Ces deux requêtes permettent de dresser un portrait fonctionnel de la portée fibre d’un pays :

La Requête 1 mesure la densité physique de la connectivité (présence territoriale).

La Requête 2 mesure la densité logique de la connectivité (interconnexion locale).

Croiser ces deux dimensions permet d’évaluer si la fibre est :

bien répartie (forte densité géographique),

bien interconnectée (forte proximité réseau).

Interprétation stratégique

Cas idéal :
Densité élevée (GeoCoveragePoints) + nombreux voisins (LocalNeighbors)
→ forte couverture fibre et interconnexion locale efficace.

Cas problématique :

Faible densité mais forte interconnexion → fibre concentrée dans quelques hubs urbains.

Forte densité mais faible interconnexion → réseau fragmenté, sous-exploité.

Cas critique :
Faible densité et faible interconnexion → réseau peu maillé, dépendant de transit international ou centralisé.

Recommandations d’Amélioration

Si la densité est faible (Req 1) → encourager le déploiement de POP régionaux ou de facilities locales.

Si la proximité est faible (Req 2) → inciter les opérateurs à plus de peering local pour réduire la latence.

Si les deux sont faibles → plan de renforcement structurel : incitations publiques, co-investissements fibre, ou hébergement d’IXP régionaux.