// Identifie les fournisseurs de transit d'un pays, compte leurs clients locaux et affiche leur rang CAIDA.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'NG', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(local_as:AS)
// Trouve la relation fournisseur-à-client (rel=1) via les données BGPKIT.
MATCH (local_as)-[:PEERS_WITH {rel: 1}]->(provider:AS)
// S'assure que le fournisseur est externe au pays.
WHERE NOT (provider)-[:COUNTRY]->(c)
// Récupère le classement CAIDA du fournisseur.
WITH provider, count(DISTINCT local_as) AS local_clients
OPTIONAL MATCH (provider)-[r:RANK]->(rank_node:Ranking {name: 'CAIDA ASRank'})
OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
RETURN provider.asn AS providerASN,
       n.name AS providerName,
       local_clients,
       r.rank AS caidaASRank
ORDER BY caidaASRank ASC, local_clients DESC
LIMIT 20;