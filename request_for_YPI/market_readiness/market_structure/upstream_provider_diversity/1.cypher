// Identifie les fournisseurs de transit pour un pays donné et compte leurs clients locaux.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
// Utilise BGPKIT (r.rel=1) pour trouver les relations Provider-to-Customer.
MATCH (as)-[r:PEERS_WITH {rel: 1}]->(provider:AS)
// S'assure que le fournisseur n'est pas lui-même local (focus sur le transit international).
WHERE NOT (provider)-[:COUNTRY]->(c)
WITH provider, count(DISTINCT as) AS localCustomers
// Récupère le nom du fournisseur pour une meilleure lisibilité.
OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
RETURN provider.asn AS providerASN,
       n.name AS providerName,
       localCustomers
ORDER BY localCustomers DESC
LIMIT 10;