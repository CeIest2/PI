// 2. Concentration des fournisseurs en amont

// 1. Trouver les AS du pays et leurs peers externes
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as_fr:AS)
MATCH (as_fr)-[:PEERS_WITH]-(peer:AS)
MATCH (peer)-[:COUNTRY]->(peer_country:Country)
WHERE peer_country <> c

// 2. Regrouper par peer externe et compter les AS domestiques connectés
RETURN peer.asn AS upstreamAS, 
       peer_country.country_code AS upstreamCountry,
       count(DISTINCT as_fr) AS clientsDomestiquesConnectes
ORDER BY clientsDomestiquesConnectes DESC
LIMIT 10