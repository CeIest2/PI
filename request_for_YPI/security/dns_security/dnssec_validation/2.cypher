// Identifies the largest access networks (by population) and checks their MANRS membership.
// The parameter $countryCode must be provided during execution (e.g., 'KE', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})<-[pop:POPULATION]-(as:AS)
// Retrieves the AS name.
OPTIONAL MATCH (as)-[:NAME]->(n:Name)
// Checks if the AS is a MANRS member.
OPTIONAL MATCH (as)-[:MEMBER_OF]->(m:Organization {name:"MANRS"})
RETURN
    as.asn AS asn,
    n.name AS name,
    pop.percent AS populationServedPercentage,
    (m IS NOT NULL) AS isManrsMember
ORDER BY populationServedPercentage DESC
LIMIT 10;