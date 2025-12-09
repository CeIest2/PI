// Récupère la part de marché de chaque AS dans un pays donné.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'CI' pour la Côte d'Ivoire).
MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
// Récupère le nom de l'AS pour une meilleure lisibilité.
OPTIONAL MATCH (as)-[:NAME]->(n:Name)
RETURN as.asn AS asn,
       n.name AS asName,
       p.population_percent AS marketSharePercent
ORDER BY marketSharePercent DESC
LIMIT 30;