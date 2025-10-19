// Analyse la distribution géographique de l'hébergement des 100 domaines ccTLD les plus populaires.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (d:DomainName)
WHERE d.name ENDS WITH '.' + toLower($countryCode)

// Se concentre sur les domaines populaires (source: Tranco) pour une analyse pertinente
MATCH (d)-[r:RANK]->(:Ranking {name:"Tranco top 1M"})
WITH d ORDER BY r.rank LIMIT 100

// Trouve le pays de l'AS qui annonce le préfixe contenant l'IP du domaine
MATCH (d)-[:RESOLVES_TO]->(:IP)<-[:ORIGINATE]-(hostingAS:AS)
MATCH (hostingAS)-[:COUNTRY]->(hostingCountry:Country)

WITH hostingCountry, count(DISTINCT d) AS domainCount
RETURN hostingCountry.country_code AS hostingCountryCode,
       domainCount
ORDER BY domainCount DESC;