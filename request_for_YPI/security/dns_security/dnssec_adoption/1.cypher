// Retrieves the 25 most popular domains for a given country, based on the percentage of DNS queries.
// The parameter $countryCode must be provided during execution (e.g., 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)
RETURN d.name AS domainName,
       q.value AS queryPercentage
ORDER BY queryPercentage DESC
LIMIT 25;