// 1. RPKI adoption rate by country (MANRS Indicator)

// 1. Find all BGP prefixes for a country
MATCH (c:Country {country_code: $countryCode})
// ASSUMPTION: (AS)-[:COUNTRY]->(Country)
MATCH (as:AS)-[:COUNTRY]->(c) 
// ASSUMPTION: (AS)-[:ORIGINATE]->(BGPPrefix)
MATCH (as)-[:ORIGINATE]->(p:BGPPrefix)
WITH c, count(DISTINCT p) AS totalPrefixes

// 2. Count those covered by RPKI
MATCH (c)<-[:COUNTRY]-(as_covered:AS)-[:ORIGINATE]->(p_covered:BGPPrefix)
// ASSUMPTION: (BGPPrefix)<-[:RESOLVES_TO]-(RPKIPrefix)
MATCH (p_covered)<-[:PART_OF]-(:RPKIPrefix)
WITH c, totalPrefixes, count(DISTINCT p_covered) AS totalCoveredPrefixes

// 3. Calculate the percentage
RETURN c.name AS country,
       totalPrefixes,
       totalCoveredPrefixes,
       CASE 
           WHEN totalPrefixes = 0 THEN 0 
           ELSE (toFloat(totalCoveredPrefixes) / totalPrefixes) * 100.0 
       END AS rpkiAdoptionPercentage
ORDER BY rpkiAdoptionPercentage DESC