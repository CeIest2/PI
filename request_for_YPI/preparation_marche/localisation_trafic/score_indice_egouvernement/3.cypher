// Vérifie le statut RPKI des préfixes annoncés par un AS hébergeant un service gouvernemental.
// PARAMETRE : $hostingASN (un ASN identifié avec la requête précédente, ex: 16276)
MATCH (hostingAS:AS {asn: $hostingASN})-[:ORIGINATE]->(p:Prefix)
MATCH (p)-[:CATEGORIZED]->(t:Tag)
WHERE t.label STARTS WITH 'RPKI'
RETURN t.label AS rpkiStatus,
       count(p) AS numberOfPrefixes
ORDER BY numberOfPrefixes DESC;