// Liste les membres MANRS d'un pays et leur importance (taille du cône client).
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)-[:MEMBER_OF]->(:Organization {name:"MANRS"})

// Jointure optionnelle avec le classement CAIDA pour obtenir la taille du cône client.
OPTIONAL MATCH (as)-[r:RANK]->(:Ranking {name:'CAIDA ASRank'})
OPTIONAL MATCH (as)-[:NAME]->(n:Name)

RETURN
  as.asn AS asn,
  n.name AS asName,
  r['cone:numberAsns'] AS customerConeSize
ORDER BY customerConeSize DESC
LIMIT 20;