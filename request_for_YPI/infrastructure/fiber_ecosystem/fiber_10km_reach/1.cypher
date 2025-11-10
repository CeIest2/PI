// Approximation de la portée fibre : densité de points géographiques des AS
// $countryCode = code du pays (ex: 'FR', 'SN', 'JP')

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
MATCH (a)-[:LOCATED_IN]->(p:Point)
RETURN c.name AS Country,
       COUNT(DISTINCT p) AS GeoCoveragePoints,
       COUNT(DISTINCT a) AS Operators
ORDER BY GeoCoveragePoints DESC;
