// Trouve les 10 AS les plus importants d'un pays qui ne sont membres d'aucun IXP local.
// Le paramètre $countryCode doit être fourni lors de l'exécution (ex: 'KE', 'BR', 'DE').
MATCH (a:AS)-[:COUNTRY]->(c:Country {country_code: $countryCode})
WHERE NOT (a)-[:MEMBER_OF]->(:IXP)
RETURN a.asn AS ASN
ORDER BY a.asn ASC
LIMIT 10;