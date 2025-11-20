// Calcule le ratio d'efficacité du peering pour un pays donné.
// Le paramètre $countryCode doit être fourni (ex: 'FR', 'SN').

MATCH (c:Country {country_code: $countryCode})

// 1. Compter le nombre total d'AS dans le pays
OPTIONAL MATCH (local_as:AS)-[:COUNTRY]->(c)
WITH c, count(DISTINCT local_as) AS totalASNs

// 2. Compter le nombre d'AS locaux membres d'au moins un IXP local
OPTIONAL MATCH (peering_as:AS)-[:COUNTRY]->(c)
MATCH (peering_as)-[:MEMBER_OF]->(ixp:IXP)-[:COUNTRY]->(c)
WITH totalASNs, count(DISTINCT peering_as) AS peeringASNs

// 3. Calculer le ratio (éviter la division par zéro)
RETURN
    totalASNs,
    peeringASNs,
    CASE
        WHEN totalASNs > 0 THEN toFloat(peeringASNs) / toFloat(totalASNs)
        ELSE 0.0
    END AS peeringEfficiencyRatio;