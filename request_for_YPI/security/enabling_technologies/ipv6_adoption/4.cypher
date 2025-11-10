// 2. Taux de serveurs (HostName) Dual-Stack (IPv4 + IPv6)

MATCH (c:Country {country_code: countryCode})

// 1. Trouver tous les serveurs (HostName) localisés dans ce pays
MATCH (h:HostName)-[:RESOLVES_TO]->(ip:IP)
MATCH (ip)-[:PART_OF]->(p)
MATCH (p)-[:COUNTRY]->(c)
WITH c, h // Obtenir les HostName uniques

// 2. Pour chaque HostName, collecter toutes les familles d'adresses (4 ou 6)
MATCH (h)-[:RESOLVES_TO]->(ip_check:IP)
WITH c, h, collect(DISTINCT ip_check.af) AS addressFamilies

// 3. Compter
WITH c, 
     count(h) AS totalServers,
     count(CASE 
         // Doit avoir 4 ET 6 dans sa liste d'AF
         WHEN (4 IN addressFamilies) AND (6 IN addressFamilies) THEN h 
         ELSE null 
     END) AS dualStackServers,
     count(CASE 
         // N'a que du 6
         WHEN NOT (4 IN addressFamilies) AND (6 IN addressFamilies) THEN h 
         ELSE null 
     END) AS ipv6OnlyServers

// 4. Calculer le pourcentage
RETURN c.name AS pays,
       totalServers,
       dualStackServers,
       ipv6OnlyServers,
       CASE 
           WHEN totalServers = 0 THEN 0 
           ELSE (toFloat(dualStackServers) / totalServers) * 100.0 
       END AS pourcentageDualStack
ORDER BY pourcentageDualStack DESC