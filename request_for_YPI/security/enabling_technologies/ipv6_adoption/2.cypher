// Identifies AS in a country without IPv6 announcements, ranked by importance.
// The parameter $countryCode must be provided during execution (e.g., 'KE', 'BE', 'CA').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)

// Check for the existence of IPv6 announcements for this AS.
OPTIONAL MATCH (as)-[:ORIGINATE]->(p:Prefix)
WHERE p.prefix CONTAINS ':'

WITH as, count(p) AS ipv6PrefixCount
// Keep only AS that have NO IPv6 announcements.
WHERE ipv6PrefixCount = 0

// Retrieve the rank and customer cone size to evaluate the importance of the AS.
MATCH (as)-[r:RANK]->(rank:Ranking {name:'CAIDA ASRank'})
OPTIONAL MATCH (as)-[:NAME]->(n:Name)

RETURN
    as.asn AS asn,
    n.name AS name,
    r['cone:numberAsns'] AS customerConeSize
ORDER BY customerConeSize DESC
LIMIT 15;