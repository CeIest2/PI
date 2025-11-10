// Liste tous les IXP d'un pays et les villes où ils sont présents.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BR', 'DE').
MATCH (i:IXP)<-[:MEMBER_OF]-(a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
OPTIONAL MATCH (a)-[:LOCATED_IN]->(f:Facility)
RETURN i.name AS IXP, COLLECT(DISTINCT f.name) AS Cities
ORDER BY IXP;