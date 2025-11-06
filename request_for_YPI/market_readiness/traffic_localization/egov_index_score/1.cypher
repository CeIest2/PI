// Trouve les domaines populaires sous le ccTLD d'un pays, classés par le % de requêtes locales.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})
MATCH (d:DomainName)-[q:QUERIED_FROM]->(c)
// Filtre pour les domaines se terminant par le ccTLD du pays (ex: '.sn')
WHERE d.name ENDS WITH '.' + toLower($countryCode)
// Utilise le rang Tranco comme critère de tri secondaire
OPTIONAL MATCH (d)-[r:RANK]->(:Ranking {name:"Tranco top 1M"})
RETURN d.name AS domainName,
       q.value AS percentageOfLocalQueries,
       r.rank AS trancoRank
ORDER BY percentageOfLocalQueries DESC, trancoRank ASC
LIMIT 25;