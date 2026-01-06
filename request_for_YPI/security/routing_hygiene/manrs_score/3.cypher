// Lists the MANRS actions implemented by members in a country.
// The parameter $countryCode must be provided during execution (e.g., 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)-[:MEMBER_OF]->(:Organization {name:"MANRS"})
MATCH (as)-[:IMPLEMENT]->(action:ManrsAction)

WITH action, count(DISTINCT as) AS implementingASNs

RETURN
  action.label AS manrsAction,
  implementingASNs
ORDER BY implementingASNs DESC;