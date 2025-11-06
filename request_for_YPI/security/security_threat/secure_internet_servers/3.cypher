// 3. Diversité des opérateurs (AS) hébergeant des serveurs
MATCH (c:Country {country_code: countryCode})

// 1. Trouver les serveurs (HostName) dans le pays (via IP/Prefix)
MATCH (h:HostName)-[:RESOLVES_TO]->(ip:IP)-[:PART_OF]->(p:BGPPrefix)-[:COUNTRY]->(c)

// 2. Trouver l'AS qui annonce (origine) ce préfixe
//    (HYPOTHÈSE: :ORIGINATE est la relation AS -> BGPPrefix)
MATCH (as:AS)-[:ORIGINATE]->(p)

// 3. (Optionnel) S'assurer que l'AS est aussi basé dans ce pays
// MATCH (as)-[:COUNTRY]->(c)

// 4. Compter
RETURN c.name AS pays,
       count(DISTINCT h) AS nombreDeServeurs,
       count(DISTINCT as) AS nombreOperateursAS
ORDER BY nombreOperateursAS DESC
