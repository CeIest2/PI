// Diversity of upstream peers

// Finds the country and its AS
MATCH (c:Country {country_code: $countryCode})
MATCH (c)<-[:COUNTRY]-(as_fr:AS)

// Finds all peers of these AS
MATCH (as_fr)-[:PEERS_WITH]-(peer:AS)

// Finds the country of these peers
MATCH (peer)-[:COUNTRY]->(peer_country:Country)

// Filters to keep only EXTERNAL peers
WHERE peer_country <> c

// Counts domestic AS and unique external peers
RETURN c.name AS country,
       count(DISTINCT as_fr) AS domesticOperators,
       count(DISTINCT peer) AS uniqueExternalPeers
ORDER BY uniqueExternalPeers DESC