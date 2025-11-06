// Compte le nombre de membres AS locaux pour chaque IXP dans un pays donné.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BR', 'DE').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(ixp:IXP)
OPTIONAL MATCH (ixp)-[:NAME]->(n:Name)
// Compte les membres (AS) de l'IXP qui sont également localisés dans le même pays.
OPTIONAL MATCH (local_as:AS)-[:COUNTRY]->(c)
MATCH (local_as)-[:MEMBER_OF]->(ixp)
WITH ixp, n, count(DISTINCT local_as) as localMembersCount
RETURN n.name as ixpName,
       localMembersCount
ORDER BY localMembersCount DESC;