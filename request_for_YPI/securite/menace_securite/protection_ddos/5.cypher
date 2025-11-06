// 3. Densité du monitoring réseau

// Trouver le pays
MATCH (c:Country {country_code: countryCode})

// Trouver les sondes localisées dans ce pays
MATCH(p:AtlasProbe)
WHERE p.country_code = countryCode

RETURN c.name AS pays,
       count(p) AS nombreSondesAtlas
ORDER BY nombreSondesAtlas DESC