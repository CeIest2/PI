// 3. Diversity of operators (AS) hosting servers
MATCH (c:Country {country_code: $countryCode})

// 1. Find servers (HostName) in the country (via IP/Prefix)
MATCH (h:HostName)-[:RESOLVES_TO]->(ip:IP)-[:PART_OF]->(p:BGPPrefix)-[:COUNTRY]->(c)

// 2. Find the AS announcing (originating) this prefix
//    (ASSUMPTION: :ORIGINATE is the relationship AS -> BGPPrefix)
MATCH (as:AS)-[:ORIGINATE]->(p)

// 3. (Optional) Ensure the AS is also based in this country
// MATCH (as)-[:COUNTRY]->(c)

// 4. Count
RETURN c.name AS country,
       count(DISTINCT h) AS numberOfServers,
       count(DISTINCT as) AS numberOfASOperators
ORDER BY numberOfASOperators DESC
