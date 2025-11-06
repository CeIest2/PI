// Compte les membres locaux et internationaux pour chaque IXP d'un pays.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(ixp:IXP)
OPTIONAL MATCH (ixp)-[:NAME]->(ixp_name:Name)
// Compte les membres qui sont membres de l'IXP.
OPTIONAL MATCH (member_as:AS)-[:MEMBER_OF]->(ixp)
// Distingue les membres locaux des membres étrangers.
WITH ixp_name, member_as, EXISTS((member_as)-[:COUNTRY]->(c)) as isLocal
RETURN  ixp_name.name AS ixpName,
        count(CASE WHEN isLocal THEN member_as END) AS localMembers,
        count(CASE WHEN NOT isLocal THEN member_as END) AS internationalMembers,
        count(member_as) AS totalMembers
ORDER BY totalMembers DESC;