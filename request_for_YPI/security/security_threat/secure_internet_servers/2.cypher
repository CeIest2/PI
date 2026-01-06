// 2. DNS infrastructure density
MATCH (c:Country {country_code: $countryCode})

// 1. Count authoritative servers
MATCH (ans:AuthoritativeNameServer)-[:ALIAS_OF]->(h_ans:HostName)-[:RESOLVES_TO]->(ip_ans:IP)
MATCH (ip_ans)-[:PART_OF]->(p_ans) // p_ans is a :Prefix, :GeoPrefix, etc.
MATCH (p_ans)-[:COUNTRY]->(c)
WITH c, count(DISTINCT ans) AS totalAuthoritativeServers

// 2. Count resolvers
MATCH (res:Resolver)<-[:RESOLVES_TO]-(h_res:HostName)-[:RESOLVES_TO]->(ip_res:IP)
MATCH (ip_res)-[:PART_OF]->(p_res) // p_res is a :Prefix, :GeoPrefix, etc.
MATCH (p_res)-[:COUNTRY]->(c)
WITH c, totalAuthoritativeServers, count(DISTINCT res) AS totalResolvers

RETURN c.name AS country,
       totalAuthoritativeServers,
       totalResolvers
ORDER BY totalAuthoritativeServers DESC, totalResolvers DESC