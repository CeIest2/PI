MATCH (:Country {country_code: $countryCode})-[:COUNTRY {reference_org: 'Google'}]-(r:Ranking)-[rr:RANK]-(hn:HostName)
WITH COUNT(DISTINCT hn) as count_total

MATCH (:Country {country_code: $countryCode})-[:COUNTRY {reference_org: 'Google'}]-(r:Ranking)-[rr:RANK]-(hn:HostName)
WHERE rr.rank <= 1000000 AND rr.origin STARTS WITH 'https'
WITH count_total, COUNT(DISTINCT hn) as count_https  // <-- Correction ici : on garde count_total

RETURN 
       CASE 
           WHEN count_total = 0 THEN 0.0 
           ELSE (toFloat(count_https) / count_total) * 100.0 
       END AS https_adoption_rate,
       count_https,
       count_total