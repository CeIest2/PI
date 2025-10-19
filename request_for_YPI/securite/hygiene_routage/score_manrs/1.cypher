// Calcule le taux de pénétration de MANRS pour un pays donné.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
WITH count(DISTINCT as) AS totalASNsInCountry

MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(manrsAS:AS)-[:MEMBER_OF]->(:Organization {name:"MANRS"})
WITH totalASNsInCountry, count(DISTINCT manrsAS) AS manrsMemberCount

RETURN
  totalASNsInCountry,
  manrsMemberCount,
  // Calcule le pourcentage d'adoption.
  round(100.0 * manrsMemberCount / totalASNsInCountry, 2) AS adoptionRatePercentage;