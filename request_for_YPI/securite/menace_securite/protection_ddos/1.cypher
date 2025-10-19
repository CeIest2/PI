// Liste les AS catégorisés comme CDN et localisés dans un pays spécifique.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'DE', 'BR').
MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
// Utilise les étiquettes de bgp.tools pour identifier les CDN.
MATCH (as)-[:CATEGORIZED]->(t:Tag {label: 'CDN'})
// Récupère le nom de l'AS pour une meilleure lisibilité.
OPTIONAL MATCH (as)-[:NAME]->(n:Name)
RETURN as.asn AS cdnASN,
       n.name AS cdnName
ORDER BY cdnName;