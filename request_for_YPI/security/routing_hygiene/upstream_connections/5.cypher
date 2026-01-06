// Presence in international IXPs

// Finds the country and its AS
MATCH (c:Country {country_code: $countryCode})
MATCH (c)<-[:COUNTRY]-(as_fr:AS)

// Finds the IXPs they are members of
MATCH (as_fr)-[:MEMBER_OF]->(ixp:IXP)

// Finds the country of the IXP
MATCH (ixp)-[:COUNTRY]->(ixp_country:Country)

// Filters to keep only IXPs abroad
WHERE ixp_country <> c

// Counts
RETURN c.name AS country,
       count(DISTINCT ixp) AS uniqueInternationalIXPs,
       count(DISTINCT as_fr) AS connectedInternationalOperators
ORDER BY connectedInternationalOperators DESC