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