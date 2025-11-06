
// 2. Taux de présence sur PeeringDB (Indicateur MANRS)
WITH 'FR' AS countryCode

MATCH (c:Country {country_code: countryCode})
MATCH (as:AS)-[:COUNTRY]->(c)
WITH c, collect(DISTINCT as) AS allASes

// Démêler et vérifier la présence d'un ID PeeringDB
UNWIND allASes AS as
// HYPOTHÈSE: (AS)-[:EXTERNAL_ID]->(PeeringdbNetID)
// Vous devrez peut-être changer :PeeringdbNetID par :PeeringdbOrgID
OPTIONAL MATCH (as)-[:EXTERNAL_ID]->(pdb:PeeringdbNetID) 

WITH c, 
     count(as) AS totalAS,
     count(pdb) AS asAvecPeeringDB // Compte les AS qui ont un lien vers un ID PDB

// Calculer le pourcentage
RETURN c.name AS pays,
       totalAS,
       asAvecPeeringDB,
       CASE 
           WHEN totalAS = 0 THEN 0 
           ELSE (toFloat(asAvecPeeringDB) / totalAS) * 100.0 
       END AS pourcentageCoordination
ORDER BY pourcentageCoordination DESC