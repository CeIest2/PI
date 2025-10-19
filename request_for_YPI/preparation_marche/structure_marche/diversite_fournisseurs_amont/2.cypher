// Mesure la dépendance moyenne des AS d'un pays envers leurs fournisseurs de transit.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
// Utilise la relation de dépendance et la métrique d'hégémonie de l'IHR.
MATCH (as)-[d:DEPENDS_ON]->(provider:AS)
// Filtre pour les dépendances significatives afin de réduire le bruit.
WHERE d.hege > 0.1 AND NOT (provider)-[:COUNTRY]->(c)
WITH provider, avg(d.hege) AS averageHegemony, count(DISTINCT as) AS dependentASNs
OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
RETURN provider.asn AS providerASN,
       n.name AS providerName,
       averageHegemony,
       dependentASNs
ORDER BY averageHegemony DESC, dependentASNs DESC
LIMIT 10;