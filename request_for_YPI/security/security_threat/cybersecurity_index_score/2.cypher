// 2. PeeringDB Presence Rate (MANRS Indicator)
WITH 'FR' AS countryCode

MATCH (c:Country {country_code: countryCode})
MATCH (as:AS)-[:COUNTRY]->(c)
WITH c, collect(DISTINCT as) AS allASes

// Unwind and check for the presence of a PeeringDB ID
UNWIND allASes AS as
// ASSUMPTION: (AS)-[:EXTERNAL_ID]->(PeeringdbNetID)
// You may need to change :PeeringdbNetID to :PeeringdbOrgID
OPTIONAL MATCH (as)-[:EXTERNAL_ID]->(pdb:PeeringdbNetID) 

WITH c, 
     count(as) AS totalAS,
     count(pdb) AS asWithPeeringDB // Counts AS with a link to a PeeringDB ID

// Calculate the percentage
RETURN c.name AS country,
       totalAS,
       asWithPeeringDB,
       CASE 
           WHEN totalAS = 0 THEN 0 
           ELSE (toFloat(asWithPeeringDB) / totalAS) * 100.0 
       END AS coordinationPercentage
ORDER BY coordinationPercentage DESC