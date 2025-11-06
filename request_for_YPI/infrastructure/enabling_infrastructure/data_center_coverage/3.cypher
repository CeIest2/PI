// Trouve les 10 AS les plus importants d'un pays qui ne sont membres d'aucun IXP local.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BR', 'DE').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
// Utilise le classement CAIDA pour mesurer l'importance de l'AS (taille du cône client).
MATCH (as)-[r:RANK]->(:Ranking {name:'CAIDA ASRank'})

// On combine les deux conditions ici dans un seul WHERE
WHERE r.`cone:numberAsns` IS NOT NULL 
  AND NOT EXISTS {
    MATCH (as)-[:MEMBER_OF]->(ixp:IXP)-[:COUNTRY]->(c)
  }

OPTIONAL MATCH (as)-[:NAME]->(n:Name)
RETURN as.asn AS asn,
       n.name AS asName,
       r.`cone:numberAsns` AS customerConeSize
ORDER BY toInteger(r.`cone:numberAsns`) DESC // Ajout de toInteger() pour un tri numérique robuste
LIMIT 10;