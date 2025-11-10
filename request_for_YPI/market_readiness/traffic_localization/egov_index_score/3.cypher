// @param: hostingASN = 16276

//
// Vérifie le statut RPKI des préfixes annoncés par un AS hébergeant un service.
//
MATCH (hostingAS:AS {asn: $hostingASN})-[:ORIGINATE]->(p:Prefix)
MATCH (p)-[:CATEGORIZED]->(t:Tag)
WHERE t.label STARTS WITH 'RPKI'
RETURN t.label AS rpkiStatus,
       count(p) AS numberOfPrefixes
ORDER BY numberOfPrefixes DESC;