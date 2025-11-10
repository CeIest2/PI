// Liste les IXP d'un pays et les data centers où ils sont situés.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'SN', 'FR', 'JP').
MATCH (i:IXP)<-[:MEMBER_OF]-(a:AS)-[:LOCATED_IN]->(f:Facility),
      (a)-[:COUNTRY]->(c:Country {country_code: $countryCode})
RETURN i.name AS IXP, COLLECT(DISTINCT f.name) AS Facilities
ORDER BY SIZE(Facilities) DESC;