// Dresse l'inventaire des actions MANRS implémentées par les membres dans un pays.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)-[:MEMBER_OF]->(:Organization {name:"MANRS"})
MATCH (as)-[:IMPLEMENT]->(action:ManrsAction)

WITH action, count(DISTINCT as) AS implementingASNs

RETURN
  action.label AS manrsAction,
  implementingASNs
ORDER BY implementingASNs DESC;