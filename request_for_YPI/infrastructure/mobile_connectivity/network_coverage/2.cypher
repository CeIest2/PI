// Couverture réseau via les infrastructures physiques (Facilities).

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:LOCATED_IN]->(f:Facility)
RETURN c.name AS Country,
       COUNT(DISTINCT f) AS InfrastructureNodes;
