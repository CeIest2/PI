// Calcule le pourcentage d'AS dans un pays qui annoncent des préfixes IPv6.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
MATCH (c:Country {country_code: countryCode})

// Trouver tous les préfixes BGP originaires d'AS de ce pays
MATCH (as:AS)-[:COUNTRY]->(c)
MATCH (as)-[:ORIGINATE]->(p:BGPPrefix)

// Compter le total, et compter ceux qui sont IPv6 (af = 6)
WITH c, 
     count(p) AS totalPrefixes,
     count(CASE WHEN p.af = 6 THEN p ELSE null END) AS ipv6Prefixes,
     count(CASE WHEN p.af = 4 THEN p ELSE null END) AS ipv4Prefixes

// Calculer le pourcentage
RETURN c.name AS pays,
       totalPrefixes,
       ipv4Prefixes,
       ipv6Prefixes,
       CASE 
           WHEN totalPrefixes = 0 THEN 0 
           ELSE (toFloat(ipv6Prefixes) / totalPrefixes) * 100.0 
       END AS pourcentagePrefixesIPv6
ORDER BY pourcentagePrefixesIPv6 DESC