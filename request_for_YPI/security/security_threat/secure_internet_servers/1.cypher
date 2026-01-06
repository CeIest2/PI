// 1. RPKI coverage rate of prefixes hosting servers


// 1. Find all unique prefixes (BGPPrefix) hosting
//    servers (HostName) in the target country.
MATCH (c:Country {country_code: $countryCode})
MATCH (h:HostName)-[:RESOLVES_TO]->(ip:IP)
MATCH (ip)-[:PART_OF]->(p:BGPPrefix) // Ensure 'p' is a BGPPrefix
MATCH (p)-[:COUNTRY]->(c)
WITH c, collect(DISTINCT p) AS all_server_prefixes

// 2. Among these prefixes, find those covered by RPKI
UNWIND all_server_prefixes AS prefix
OPTIONAL MATCH (prefix)<-[:PART_OF]-(rpki:RPKIPrefix)
WITH c, 
     count(prefix) AS totalPrefixes, 
     count(DISTINCT rpki) AS coveredPrefixes // Count prefixes with at least one ROA

// 3. Calculate the percentage
RETURN c.name AS country,
       totalPrefixes,
       coveredPrefixes,
       (toFloat(coveredPrefixes) / totalPrefixes) * 100.0 AS rpkiCoveragePercentage
ORDER BY rpkiCoveragePercentage DESC