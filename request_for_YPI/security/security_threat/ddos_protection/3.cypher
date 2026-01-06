// Identifies popular domains in a country and checks if they are hosted by a CDN.
// The parameter $countryCode must be provided during execution (e.g., 'KE', 'DE', 'BR').
// Finds the most queried domains from the country.
MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)
WITH d, q.value AS queryPercentage ORDER BY queryPercentage DESC LIMIT 20
// Finds the AS announcing the IP of these domains.
MATCH (d)-[:RESOLVES_TO]->(:IP)-[:ORIGINATE]->(hostAS:AS)
// Checks if this AS is a CDN.
WHERE (hostAS)-[:CATEGORIZED]->(:Tag {label:"CDN"})
OPTIONAL MATCH (hostAS)-[:NAME]->(n:Name)
RETURN d.name AS popularDomain,
       hostAS.asn AS hostingCdnASN,
       n.name AS hostingCdnName,
       queryPercentage
ORDER BY queryPercentage DESC;