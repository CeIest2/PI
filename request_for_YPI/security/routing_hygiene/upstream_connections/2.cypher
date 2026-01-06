// Analyzes the distribution of a country's transit providers by CAIDA rank category.
// The parameter $countryCode must be provided during execution (e.g., 'NG', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(local_as:AS)
MATCH (local_as)-[:PEERS_WITH {rel: 1}]->(provider:AS)
WHERE NOT (provider)-[:COUNTRY]->(c)

// Retrieves the CAIDA ranking of each unique provider.
WITH DISTINCT provider
MATCH (provider)-[r:RANK]->(:Ranking {name: 'CAIDA ASRank'})

// Calculates the category and passes the provider in a single WITH
WITH provider,
     CASE
        WHEN r.rank <= 100 THEN 'A) Top 100 (Internet Core)'
        WHEN r.rank > 100 AND r.rank <= 500 THEN 'B) Top 101-500 (Major)'
        WHEN r.rank > 500 AND r.rank <= 2000 THEN 'C) Top 501-2000 (Important)'
        ELSE 'D) Beyond 2000 (Regional/Niche)'
     END AS providerTier

// Counts the number of providers in each category.
RETURN providerTier,
       count(provider) AS numberOfProviders
ORDER BY providerTier ASC;