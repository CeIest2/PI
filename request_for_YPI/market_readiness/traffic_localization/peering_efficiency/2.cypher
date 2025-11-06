// Calcule le ratio des AS locaux qui peerent sur un IXP local.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'NG', 'US').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
WITH count(DISTINCT as) AS totalASNs, c

// Sous-requête pour compter les AS qui peerent localement.
CALL {
    WITH c
    MATCH (ixp:IXP)-[:COUNTRY]->(c)
    MATCH (local_as:AS)-[:COUNTRY]->(c)
    MATCH (local_as)-[:MEMBER_OF]->(ixp)
    RETURN count(DISTINCT local_as) AS peeringASNs
}

RETURN totalASNs,
       peeringASNs,
       // Calcule et formate le ratio en pourcentage.
       round(100.0 * peeringASNs / totalASNs, 2) AS peeringEfficiencyRatio;