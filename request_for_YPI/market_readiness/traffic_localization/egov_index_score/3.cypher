// Query 3: RPKI Status
MATCH (hostingAS:AS {asn: $hostingASN})-[:ORIGINATE]->(p:Prefix)
MATCH (p)-[:CATEGORIZED]->(t:Tag)
WHERE t.label STARTS WITH 'RPKI'
RETURN t.label AS rpkiStatus,
       count(p) AS numberOfPrefixes
ORDER BY numberOfPrefixes DESC;