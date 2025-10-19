// Calcule le pourcentage d'AS dans un pays qui annoncent des préfixes IPv6.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
WITH count(DISTINCT as) AS totalASNs, c

MATCH (c)<-[:COUNTRY]-(as_v6:AS)-[:ORIGINATE]->(p:Prefix)
WHERE p.prefix CONTAINS ':'
WITH totalASNs, count(DISTINCT as_v6) AS ipv6EnabledASNs

RETURN
    totalASNs,
    ipv6EnabledASNs,
    // Calcule le ratio en pourcentage.
    round(100.0 * ipv6EnabledASNs / totalASNs, 2) AS adoptionRatePercentage;