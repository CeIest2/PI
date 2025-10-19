// Calcule le nombre d'AS locaux membres d'un IXP local.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'NG', 'US').
MATCH (c:Country {country_code: $countryCode})
// Trouve les IXP dans le pays cible.
MATCH (ixp:IXP)-[:COUNTRY]->(c)
// Trouve les AS dans ce même pays qui sont membres de ces IXP.
MATCH (as:AS)-[:COUNTRY]->(c)
MATCH (as)-[:MEMBER_OF]->(ixp)
RETURN count(DISTINCT as.asn) AS numberOfPeeringASNs;