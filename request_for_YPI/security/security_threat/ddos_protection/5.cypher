// 3. Network Monitoring Density

// Find the country
MATCH (c:Country {country_code: $countryCode})

// Find probes located in this country
MATCH (p:AtlasProbe)
WHERE p.country_code = $countryCode
RETURN c.name AS country,
       count(p) AS numberOfAtlasProbes
ORDER BY numberOfAtlasProbes DESC