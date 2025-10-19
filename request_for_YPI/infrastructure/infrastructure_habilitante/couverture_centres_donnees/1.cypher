// Liste tous les IXP d'un pays et les villes où ils sont présents.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BR', 'DE').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(ixp:IXP)
// Trouve les installations physiques (data centers) où l'IXP est présent.
MATCH (ixp)-[:LOCATED_IN]->(f:Facility)
WITH ixp, collect(DISTINCT f.city) AS cities
// Récupère le nom officiel de l'IXP.
OPTIONAL MATCH (ixp)-[:NAME]->(n:Name)
RETURN n.name AS ixpName,
       ixp.id_peeringdb AS peeringdbID,
       cities
ORDER BY ixpName;