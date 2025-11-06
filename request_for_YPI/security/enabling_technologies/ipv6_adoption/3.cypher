// 3. Disponibilité IPv6 de l'infrastructure DNS
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
MATCH (c:Country {country_code: countryCode})

// 1. Compter les serveurs faisant autorité accessibles en IPv6
MATCH (ans:AuthoritativeNameServer)<-[:ALIAS_OF]-(h_ans:HostName)-[:RESOLVES_TO]->(ip_ans:IP)
MATCH (ip_ans)-[:PART_OF]->(p_ans)
MATCH (p_ans)-[:COUNTRY]->(c)
WITH c, 
     count(DISTINCT ans) AS totalANS,
     count(DISTINCT CASE WHEN ip_ans.af = 6 THEN ans ELSE null END) AS ipv6ReadyANS

// 2. Compter les résolveurs accessibles en IPv6
MATCH (res:Resolver)<-[:RESOLVES_TO]-(h_res:HostName)-[:RESOLVES_TO]->(ip_res:IP)
MATCH (ip_res)-[:PART_OF]->(p_res)
MATCH (p_res)-[:COUNTRY]->(c)
WITH c, totalANS, ipv6ReadyANS,
     count(DISTINCT res) AS totalResolvers,
     count(DISTINCT CASE WHEN ip_res.af = 6 THEN res ELSE null END) AS ipv6ReadyResolvers

// 3. Retourner les résultats
RETURN c.name AS pays,
       totalANS,
       ipv6ReadyANS,
       totalResolvers,
       ipv6ReadyResolvers