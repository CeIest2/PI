// Liste les IXP d'un pays et les data centers où ils sont situés.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(ixp:IXP)
// Trouve le nom de l'IXP et le data center où il est hébergé via PeeringDB.
OPTIONAL MATCH (ixp)-[:NAME]->(ixp_name:Name)
OPTIONAL MATCH (ixp)-[:LOCATED_IN]->(fac:Facility)-[:NAME]->(fac_name:Name)
RETURN  ixp_name.name AS ixpName,
        collect(DISTINCT fac_name.name) AS facilities
ORDER BY ixpName;