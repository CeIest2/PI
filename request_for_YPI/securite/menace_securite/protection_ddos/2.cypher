// Mesure le pourcentage de la population d'un pays desservi par des AS de type CDN.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
MATCH (as)-[:CATEGORIZED]->(t:Tag {label: 'CDN'})
OPTIONAL MATCH (as)-[:NAME]->(n:Name)
RETURN as.asn AS cdnASN,
       n.name AS cdnName,
       p.percent AS populationServedPercentage
ORDER BY populationServedPercentage DESC;