// Analyse la répartition des fournisseurs de transit d'un pays par catégorie de rang CAIDA.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'NG', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(local_as:AS)
MATCH (local_as)-[:PEERS_WITH {rel: 1}]->(provider:AS)
WHERE NOT (provider)-[:COUNTRY]->(c)

// Récupère le classement CAIDA de chaque fournisseur unique.
WITH DISTINCT provider
MATCH (provider)-[r:RANK]->(:Ranking {name: 'CAIDA ASRank'})

// On calcule la catégorie et on passe le provider dans un seul WITH
WITH provider,
     CASE
        WHEN r.rank <= 100 THEN 'A) Top 100 (Coeur Internet)'
        WHEN r.rank > 100 AND r.rank <= 500 THEN 'B) Top 101-500 (Majeur)'
        WHEN r.rank > 500 AND r.rank <= 2000 THEN 'C) Top 501-2000 (Important)'
        ELSE 'D) Au-delà de 2000 (Régional/Niche)'
     END AS providerTier

// On compte le nombre de fournisseurs dans chaque catégorie.
RETURN providerTier,
       count(provider) AS numberOfProviders
ORDER BY providerTier ASC;