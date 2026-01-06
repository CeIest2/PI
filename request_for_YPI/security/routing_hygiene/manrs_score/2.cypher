// Lists the MANRS members in a country and their importance (customer cone size).
// The parameter $countryCode must be provided during execution (e.g., 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)-[:MEMBER_OF]->(:Organization {name:"MANRS"})

// Optional join with the CAIDA ranking to get the customer cone size.
OPTIONAL MATCH (as)-[r:RANK]->(:Ranking {name:'CAIDA ASRank'})
OPTIONAL MATCH (as)-[:NAME]->(n:Name)

RETURN
  as.asn AS asn,
  n.name AS asName,
  r['cone:numberAsns'] AS customerConeSize
ORDER BY customerConeSize DESC
LIMIT 20;