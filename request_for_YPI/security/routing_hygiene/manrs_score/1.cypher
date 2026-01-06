// Calculates the MANRS penetration rate for a given country.
// The parameter $countryCode must be provided during execution (e.g., 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
WITH count(DISTINCT as) AS totalASNsInCountry

MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(manrsAS:AS)-[:MEMBER_OF]->(:Organization {name:"MANRS"})
WITH totalASNsInCountry, count(DISTINCT manrsAS) AS manrsMemberCount

RETURN
  totalASNsInCountry,
  manrsMemberCount,
  // Calculates the adoption percentage.
  round(100.0 * manrsMemberCount / totalASNsInCountry, 2) AS adoptionRatePercentage;