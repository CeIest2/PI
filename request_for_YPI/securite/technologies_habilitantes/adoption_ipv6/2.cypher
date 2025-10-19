// Identifie les AS d'un pays sans annonce IPv6, classés par importance.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BE', 'CA').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)

// Vérifie l'existence d'annonces IPv6 pour cet AS.
OPTIONAL MATCH (as)-[:ORIGINATE]->(p:Prefix)
WHERE p.prefix CONTAINS ':'

WITH as, count(p) AS ipv6PrefixCount
// Garde uniquement les AS qui n'ont AUCUNE annonce IPv6.
WHERE ipv6PrefixCount = 0

// Récupère le rang et la taille du cône client pour évaluer l'importance de l'AS.
MATCH (as)-[r:RANK]->(rank:Ranking {name:'CAIDA ASRank'})
OPTIONAL MATCH (as)-[:NAME]->(n:Name)

RETURN
    as.asn AS asn,
    n.name AS name,
    r['cone:numberAsns'] AS customerConeSize
ORDER BY customerConeSize DESC
LIMIT 15;