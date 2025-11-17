// 4. Diversité des points d'échange (IXP)

MATCH (c:Country {country_code: $countryCode})

// 1. Trouver les IXP localisés dans le pays
MATCH (ixp:IXP)-[:COUNTRY]->(c)

// 2. Trouver les AS (pas les Organizations) qui sont membres de ces IXP
// C'est le changement clé : on utilise (as:AS)
MATCH (as:AS)-[:MEMBER_OF]->(ixp)

// 3. (Optionnel) Si vous voulez remonter à l'organisation propriétaire de l'AS
//    et s'assurer qu'elle est aussi du même pays
// MATCH (o:Organization)-[:COUNTRY]->(c)
// MATCH (o)-[:OWNS_OR_MANAGES]-(as) // (Vous devez trouver ce nom de relation)

// 4. Compter les entités
RETURN c.name AS pays,
       count(DISTINCT ixp) AS nombreIXP,
       count(DISTINCT as) AS nombreASMembres
ORDER BY nombreIXP DESC
