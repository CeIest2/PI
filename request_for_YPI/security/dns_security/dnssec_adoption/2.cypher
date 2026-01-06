// Retrieves domains from the Tranco top 1M resolved to IPs hosted in the target country.
// The parameter $countryCode must be provided during execution (e.g., 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)<-[:ORIGINATE]-(:Prefix)<-[:MEMBER_OF]-(:IP)<-[:RESOLVES_TO]-(d:DomainName)
// Uses the Tranco ranking to filter by popularity
MATCH (d)-[r:RANK]->(rk:Ranking)
WHERE rk.name CONTAINS 'Tranco'
RETURN d.name AS domainName,
       r.rank AS popularityRank,
       as.asn AS hostingASN
ORDER BY r.rank ASC
LIMIT 25;