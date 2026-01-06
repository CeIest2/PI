// 1. Diversity of Operators and Prefixes by Country
// Define the target country code (e.g., 'FR' for France)

// Find the country
MATCH (c:Country {country_code: $countryCode})

// Find organizations based in this country
MATCH (a:AS)-[:COUNTRY]->(c)

MATCH (a)-[:ORIGINATE]->(p:BGPPrefix)

WITH c, count(DISTINCT p) AS totalPrefixes
// 2. Count only prefixes covered by RPKI
MATCH (c)<-[:COUNTRY]-(a_covered:AS)-[:ORIGINATE]->(p_covered:BGPPrefix)
MATCH (p_covered)<-[:ROUTE_ORIGIN_AUTHORIZATION]-(b)
WITH c, totalPrefixes, count(DISTINCT p_covered) AS coveredPrefixes

// 3. Calculate the percentage
RETURN c.name AS country,
       totalPrefixes,
       coveredPrefixes,
       (toFloat(coveredPrefixes) / totalPrefixes) * 100.0 AS rpkiCoveragePercentage
ORDER BY rpkiCoveragePercentage DESC