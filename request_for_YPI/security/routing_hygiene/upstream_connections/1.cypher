// Identifies the transit providers of a country, counts their local clients, and displays their CAIDA rank.
// The parameter $countryCode must be provided during execution (e.g., 'NG', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(local_as:AS)
// Finds the provider-to-customer relationship (rel=1) via BGPKIT data.
MATCH (local_as)-[:PEERS_WITH {rel: 1}]->(provider:AS)
// Ensures the provider is external to the country.
WHERE NOT (provider)-[:COUNTRY]->(c)
// Retrieves the CAIDA ranking of the provider.
WITH provider, count(DISTINCT local_as) AS local_clients
OPTIONAL MATCH (provider)-[r:RANK]->(rank_node:Ranking {name: 'CAIDA ASRank'})
OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
RETURN provider.asn AS providerASN,
       n.name AS providerName,
       local_clients,
       r.rank AS caidaASRank
ORDER BY caidaASRank ASC, local_clients DESC
LIMIT 20;