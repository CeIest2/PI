// Identifie les domaines populaires dans un pays et vérifie s'ils sont hébergés par un CDN.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'DE', 'BR').
// Trouve les domaines les plus interrogés depuis le pays.
MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)
WITH d, q.value AS queryPercentage ORDER BY queryPercentage DESC LIMIT 20
// Trouve l'AS qui annonce l'IP de ces domaines.
MATCH (d)-[:RESOLVES_TO]->(:IP)-[:ORIGINATE]->(hostAS:AS)
// Vérifie si cet AS est un CDN.
WHERE (hostAS)-[:CATEGORIZED]->(:Tag {label:"CDN"})
OPTIONAL MATCH (hostAS)-[:NAME]->(n:Name)
RETURN d.name AS popularDomain,
       hostAS.asn AS hostingCdnASN,
       n.name AS hostingCdnName,
       queryPercentage
ORDER BY queryPercentage DESC;