// Calcule le pourcentage d'AS membres de MANRS dans un pays donné.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})
// Compte le nombre total d'AS dans le pays.
OPTIONAL MATCH (as:AS)-[:COUNTRY]->(c)
WITH c, count(DISTINCT as) AS totalASNs
// Compte le nombre d'AS membres de MANRS dans ce même pays.
OPTIONAL MATCH (manrs_as:AS)-[:COUNTRY]->(c)
WHERE (manrs_as)-[:MEMBER_OF]->(:Organization {name:"MANRS"})
WITH totalASNs, count(DISTINCT manrs_as) AS manrsASNs
RETURN
    manrsASNs,
    totalASNs,
    CASE
        WHEN totalASNs > 0 THEN (toFloat(manrsASNs) / totalASNs) * 100
        ELSE 0
    END AS manrsAdoptionPercentage;