// Compte le nombre de membres AS locaux pour chaque IXP dans un pays donné.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BR', 'DE').
MATCH (a:AS)-[:MEMBER_OF]->(i:IXP), (a)-[:COUNTRY]->(c:Country {country_code: $countryCode})
RETURN i.name AS IXP, COUNT(DISTINCT a) AS LocalMembers
ORDER BY LocalMembers DESC;MATCH (a:AS)-[:MEMBER_OF]->(i:IXP), (a)-[:COUNTRY]->(c:Country {country_code: $countryCode})
