// 1. Taux de couverture RPKI des préfixes hébergeant des serveurs


// 1. Trouver tous les préfixes uniques (BGPPrefix) qui hébergent
//    des serveurs (HostName) dans le pays cible.
MATCH (c:Country {country_code: $countryCode})
MATCH (h:HostName)-[:RESOLVES_TO]->(ip:IP)
MATCH (ip)-[:PART_OF]->(p:BGPPrefix) // S'assurer que 'p' est un BGPPrefix
MATCH (p)-[:COUNTRY]->(c)
WITH c, collect(DISTINCT p) AS all_server_prefixes

// 2. Parmi ces préfixes, trouver ceux qui sont couverts par RPKI
UNWIND all_server_prefixes AS prefix
OPTIONAL MATCH (prefix)<-[:PART_OF]-(rpki:RPKIPrefix)
WITH c, 
     count(prefix) AS totalPrefixes, 
     count(DISTINCT rpki) AS coveredPrefixes // Compte les préfixes ayant au moins un ROA

// 3. Calculer le pourcentage
RETURN c.name AS pays,
       totalPrefixes,
       coveredPrefixes,
       (toFloat(coveredPrefixes) / totalPrefixes) * 100.0 AS pourcentageCouvertureRPKI
ORDER BY pourcentageCouvertureRPKI DESC