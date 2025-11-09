// Couverture réseau via les points géographiques déclarés.

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:LOCATED_IN]->(p:Point)
RETURN c.name AS Country,
       COUNT(DISTINCT p) AS GeoCoveragePoints;
