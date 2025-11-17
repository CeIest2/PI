// 3. Présence dans les IXP internationaux

// 1. Trouver le pays et ses AS
MATCH (c:Country {country_code: $countryCode})
MATCH (c)<-[:COUNTRY]-(as_fr:AS)

// 2. Trouver les IXP dont ils sont membres
MATCH (as_fr)-[:MEMBER_OF]->(ixp:IXP)

// 3. Trouver le pays de l'IXP
MATCH (ixp)-[:COUNTRY]->(ixp_country:Country)

// 4. Filtrer pour ne garder que les IXP à l'étranger
WHERE ixp_country <> c

// 5. Compter
RETURN c.name AS pays,
       count(DISTINCT ixp) AS ixpInternationauxUniques,
       count(DISTINCT as_fr) AS operateursConnectesInternational
ORDER BY operateursConnectesInternational DESC