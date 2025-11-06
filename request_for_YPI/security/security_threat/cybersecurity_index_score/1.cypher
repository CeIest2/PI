// 1. Taux d'adoption RPKI par pays (Indicateur MANRS)

// 1. Trouver tous les préfixes BGP pour un pays
MATCH (c:Country {country_code: countryCode})
// HYPOTHÈSE: (AS)-[:COUNTRY]->(Country)
MATCH (as:AS)-[:COUNTRY]->(c) 
// HYPOTHÈSE: (AS)-[:ORIGINATE]->(BGPPrefix)
MATCH (as)-[:ORIGINATE]->(p:BGPPrefix)
WITH c, count(DISTINCT p) AS totalPrefixes

// 2. Compter ceux qui sont couverts par RPKI
MATCH (c)<-[:COUNTRY]-(as_covered:AS)-[:ORIGINATE]->(p_covered:BGPPrefix)
// HYPOTHÈSE: (BGPPrefix)<-[:RESOLVES_TO]-(RPKIPrefix)
MATCH (p_covered)<-[:PART_OF]-(:RPKIPrefix)
WITH c, totalPrefixes, count(DISTINCT p_covered) AS totalCoveredPrefixes

// 3. Calculer le pourcentage
RETURN c.name AS pays,
       totalPrefixes,
       totalCoveredPrefixes,
       CASE 
           WHEN totalPrefixes = 0 THEN 0 
           ELSE (toFloat(totalCoveredPrefixes) / totalPrefixes) * 100.0 
       END AS pourcentageAdoptionRPKI
ORDER BY pourcentageAdoptionRPKI DESC