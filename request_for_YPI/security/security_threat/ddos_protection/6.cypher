// 1. Diversité des Opérateurs et Préfixes par Pays
// Définir le code pays cible (ex: 'FR' pour la France)

// Trouver le pays
MATCH (c:Country {country_code: $countryCode})

// Trouver les organisations basées dans ce pays
MATCH (a:AS)-[:COUNTRY]->(c)

MATCH (a)-[:ORIGINATE]->(p:BGPPrefix)

WITH c, count(DISTINCT p) AS totalPrefixes
// 2. Compter uniquement les préfixes couverts par RPKI
MATCH (c)<-[:COUNTRY]-(a_couvert:AS)-[:ORIGINATE]->(p_couvert:BGPPrefix)
MATCH (p_couvert)<-[:ROUTE_ORIGIN_AUTHORIZATION]-(b)
WITH c, totalPrefixes, count(DISTINCT p_couvert) AS prefixesCouverts

// 3. Calculer le pourcentage
RETURN c.name AS pays,
       totalPrefixes,
       prefixesCouverts,
       (toFloat(prefixesCouverts) / totalPrefixes) * 100.0 AS pourcentageCouvertureRPKI
ORDER BY pourcentageCouvertureRPKI DESC