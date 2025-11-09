// Approxime la proximité fibre : nombre de voisins réseau locaux.
// Plus un AS a de connexions PEERS_WITH, plus il a une "portée" courte.

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:PEERS_WITH]-(b:AS)
RETURN a.asn AS ASN,
       COUNT(DISTINCT b) AS LocalNeighbors
ORDER BY LocalNeighbors DESC
LIMIT 20;

