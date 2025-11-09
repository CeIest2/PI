// Mesure la couverture réseau via le peering entre AS locaux.

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:PEERS_WITH]-(b:AS)
RETURN c.name AS Country,
       COUNT(DISTINCT b) AS TotalPeerings;
