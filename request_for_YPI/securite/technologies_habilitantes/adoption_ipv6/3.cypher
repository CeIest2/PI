// Vérifie la disponibilité IPv6 des domaines les plus populaires d'un pays.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)

// Ordonne par popularité et prend le top 20.
WITH d, q.value AS popularity ORDER BY popularity DESC LIMIT 20

// Récupère toutes les adresses IP associées au domaine.
MATCH (d)-[:RESOLVES_TO]->(ip:IP)
WITH d, popularity, collect(ip.address) AS ipAddresses

RETURN
    d.name AS domain,
    // Vérifie si AU MOINS UNE des adresses IP est une adresse IPv6.
    ANY(addr IN ipAddresses WHERE addr CONTAINS ':') AS isIPv6Enabled
ORDER BY popularity DESC;