// Récupère les 25 domaines les plus populaires pour un pays donné, basés sur le % de requêtes DNS.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)
RETURN d.name AS domainName,
       q.value AS queryPercentage
ORDER BY queryPercentage DESC
LIMIT 25;