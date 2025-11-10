// Récupère les domaines du top 1M de Tranco résolus vers des IP hébergées dans le pays cible.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)<-[:ORIGINATE]-(:Prefix)<-[:MEMBER_OF]-(:IP)<-[:RESOLVES_TO]-(d:DomainName)
// Utilise le classement Tranco pour filtrer par popularité
MATCH (d)-[r:RANK]->(rk:Ranking)
WHERE rk.name CONTAINS 'Tranco'
RETURN d.name AS domainName,
       r.rank AS popularityRank,
       as.asn AS hostingASN
ORDER BY r.rank ASC
LIMIT 25;