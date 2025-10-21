// Tracks the number of new ASNs joining a local IXP for the first time each year.
// The $countryCode parameter must be provided at execution.
// PREREQUISITE: The :MEMBER_OF relationship must have a temporal property (e.g., .timestamp in ms).
MATCH (c:Country {country_code: $countryCode})
MATCH (as:AS)-[:COUNTRY]->(c)
MATCH (ixp:IXP)-[:COUNTRY]->(c)
MATCH (as)-[r:MEMBER_OF]->(ixp)
WHERE r.timestamp IS NOT NULL

// For each AS, find its earliest join date across all local IXPs
WITH as, min(r.timestamp) AS firstJoinTimestamp

// Group by the year of that first join date
WITH datetime({epochMillis: firstJoinTimestamp}).year AS joinYear

RETURN
    joinYear,
    count(joinYear) AS newPeerAsnsCount
ORDER BY joinYear ASC;