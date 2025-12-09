// Query 2: Hosting Analysis (Fix: relation IP->Prefix générique)
MATCH (d:DomainName {name: $domainName})
MATCH (d)-[:RESOLVES_TO]->(ip:IP)

// UTILISATION D'UNE RELATION ANONYME '-->' pour contourner l'erreur de nom
MATCH (ip)-->(p:Prefix)

MATCH (hostingAS:AS)-[:ORIGINATE]->(p)

OPTIONAL MATCH (hostingAS)-[:NAME]->(n:Name)
OPTIONAL MATCH (hostingAS)-[:COUNTRY]->(hostingCountry:Country)

RETURN DISTINCT
       hostingAS.asn AS hostingASN,
       n.name AS hostingASName,
       hostingCountry.country_code AS hostingASCountry,
       (hostingCountry.country_code = $countryCode) AS isHostedLocally
LIMIT 10;