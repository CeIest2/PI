// Couverture réseau : nombre d'AS enregistrés dans le pays.

MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
RETURN c.name AS Country,
       COUNT(DISTINCT a) AS ASN_Count;

