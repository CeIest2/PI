// Calcule l'indice Herfindahl-Hirschman (HHI) pour un pays donné.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'CI').
MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
// Calcule la somme des carrés des parts de marché (en pourcentage).
WITH sum(p.population_percent^2) AS hhi
RETURN hhi,
    CASE
        WHEN hhi < 1500 THEN 'Marché Concurrentiel'
        WHEN hhi >= 1500 AND hhi <= 2500 THEN 'Marché Modérément Concentré'
        ELSE 'Marché Très Concentré'
    END AS marketConcentration;