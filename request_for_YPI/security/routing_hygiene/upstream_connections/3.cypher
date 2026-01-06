// Concentration of upstream providers

// Finds the country's AS and their external peers
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as_fr:AS)
MATCH (as_fr)-[:PEERS_WITH]-(peer:AS)
MATCH (peer)-[:COUNTRY]->(peer_country:Country)
WHERE peer_country <> c

// Groups by external peer and counts connected domestic AS
RETURN peer.asn AS upstreamAS, 
       peer_country.country_code AS upstreamCountry,
       count(DISTINCT as_fr) AS connectedDomesticClients
ORDER BY connectedDomesticClients DESC
LIMIT 10