// Identifies local ASNs that do not peer at any local IXP, ordered by importance.
// The $countryCode parameter must be provided at execution.
MATCH (c:Country {country_code: $countryCode})

// Find all local ASNs
MATCH (localAS:AS)-[:COUNTRY]->(c)

// Filter to keep only those NOT connected to a local IXP
WHERE NOT EXISTS {
  MATCH (localAS)-[:MEMBER_OF]->(:IXP)-[:COUNTRY]->(c)
}

// Get AS Rank to sort by importance (lower rank is more important)
OPTIONAL MATCH (localAS)-[r:RANK]->(:Ranking {name:'CAIDA ASRank'})
OPTIONAL MATCH (localAS)-[:NAME]->(n:Name)

RETURN
    localAS.asn AS asn,
    n.name AS asName,
    r.rank AS caidaRank
ORDER BY caidaRank ASC
LIMIT 20;