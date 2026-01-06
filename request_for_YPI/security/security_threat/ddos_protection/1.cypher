// Lists AS categorized as CDN and located in a specific country.
// The parameter $countryCode must be provided during execution (e.g., 'KE', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
// Uses bgp.tools tags to identify CDNs.
MATCH (as)-[:CATEGORIZED]->(t:Tag {label: 'CDN'})
// Retrieves the AS name for better readability.
OPTIONAL MATCH (as)-[:NAME]->(n:Name)
RETURN as.asn AS cdnASN,
       n.name AS cdnName
ORDER BY cdnName;