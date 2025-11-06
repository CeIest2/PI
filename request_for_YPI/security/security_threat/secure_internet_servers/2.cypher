
// 2. Densité de l'infrastructure DNS
MATCH (c:Country {country_code: countryCode})

// 1. Compter les serveurs faisant autorité
MATCH (ans:AuthoritativeNameServer)-[:ALIAS_OF]->(h_ans:HostName)-[:RESOLVES_TO]->(ip_ans:IP)
MATCH (ip_ans)-[:PART_OF]->(p_ans) // p_ans est un :Prefix, :GeoPrefix, etc.
MATCH (p_ans)-[:COUNTRY]->(c)
WITH c, count(DISTINCT ans) AS totalServeursAutorite

// 2. Compter les résolveurs
MATCH (res:Resolver)<-[:RESOLVES_TO]-(h_res:HostName)-[:RESOLVES_TO]->(ip_res:IP)
MATCH (ip_res)-[:PART_OF]->(p_res) // p_res est un :Prefix, :GeoPrefix, etc.
MATCH (p_res)-[:COUNTRY]->(c)
WITH c, totalServeursAutorite, count(DISTINCT res) AS totalResolveurs

RETURN c.name AS pays,
       totalServeursAutorite,
       totalResolveurs
ORDER BY totalServeursAutorite DESC, totalResolveurs DESC