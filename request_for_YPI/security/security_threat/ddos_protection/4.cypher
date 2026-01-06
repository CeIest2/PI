// 4. Diversity of Internet Exchange Points (IXP)

MATCH (c:Country {country_code: $countryCode})

// 1. Find IXPs located in the country
MATCH (ixp:IXP)-[:COUNTRY]->(c)

// 2. Find AS (not Organizations) that are members of these IXPs
// This is the key change: using (as:AS)
MATCH (as:AS)-[:MEMBER_OF]->(ixp)

// 3. (Optional) If you want to trace back to the organization owning the AS
//    and ensure it is also from the same country
// MATCH (o:Organization)-[:COUNTRY]->(c)
// MATCH (o)-[:OWNS_OR_MANAGES]-(as) // (You need to find this relationship name)

// 4. Count the entities
RETURN c.name AS country,
       count(DISTINCT ixp) AS numberOfIXPs,
       count(DISTINCT as) AS numberOfASMembers
ORDER BY numberOfIXPs DESC
