// Query 1: Top Local Domains
MATCH (c:Country {country_code: $countryCode})
MATCH (d:DomainName)-[q:QUERIED_FROM]->(c)
WHERE d.name ENDS WITH '.' + toLower($countryCode)
OPTIONAL MATCH (d)-[r:RANK]->(:Ranking {name:"Tranco top 1M"})
RETURN d.name AS domainName,
       q.value AS percentageOfLocalQueries,
       r.rank AS trancoRank
ORDER BY percentageOfLocalQueries DESC, trancoRank ASC
LIMIT 25;