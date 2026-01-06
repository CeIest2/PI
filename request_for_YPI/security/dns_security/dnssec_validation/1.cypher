// Calculates the percentage of MANRS member AS in a given country.
// The parameter $countryCode must be provided during execution (e.g., 'KE', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})
// Counts the total number of AS in the country.
OPTIONAL MATCH (as:AS)-[:COUNTRY]->(c)
WITH c, count(DISTINCT as) AS totalASNs
// Counts the number of MANRS member AS in the same country.
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