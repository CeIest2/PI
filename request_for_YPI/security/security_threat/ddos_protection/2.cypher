// Measures the percentage of a country's population served by CDN-type AS.
// The parameter $countryCode must be provided during execution (e.g., 'KE', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
MATCH (as)-[:CATEGORIZED]->(t:Tag {label: 'CDN'})
OPTIONAL MATCH (as)-[:NAME]->(n:Name)
RETURN as.asn AS cdnASN,
       n.name AS cdnName,
       p.percent AS populationServedPercentage
ORDER BY populationServedPercentage DESC;