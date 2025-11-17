// 1. Diversité des peers en amont

// 1. Trouver le pays et ses AS
MATCH (c:Country {country_code: $countryCode})
MATCH (c)<-[:COUNTRY]-(as_fr:AS)

// 2. Trouver tous les peers de ces AS
MATCH (as_fr)-[:PEERS_WITH]-(peer:AS)

// 3. Trouver le pays de ces peers
MATCH (peer)-[:COUNTRY]->(peer_country:Country)

// 4. Filtrer pour ne garder que les peers EXTERNES
WHERE peer_country <> c

// 5. Compter les AS domestiques et les peers externes uniques
RETURN c.name AS pays,
       count(DISTINCT as_fr) AS operateursDomestiques,
       count(DISTINCT peer) AS peersExternesUniques
ORDER BY peersExternesUniques DESC