// Calculates the percentage of AS in a country that announce IPv6 prefixes.
// The parameter $countryCode must be provided during execution (e.g., 'KE', 'BE', 'CA').
MATCH (c:Country {country_code: $countryCode})

// Find all BGP prefixes originated by AS in this country
MATCH (as:AS)-[:COUNTRY]->(c)
MATCH (as)-[:ORIGINATE]->(p:BGPPrefix)

// Count the total, and count those that are IPv6 (af = 6)
WITH c, 
     count(p) AS totalPrefixes,
     count(CASE WHEN p.af = 6 THEN p ELSE null END) AS ipv6Prefixes,
     count(CASE WHEN p.af = 4 THEN p ELSE null END) AS ipv4Prefixes

// Calculate the percentage
RETURN c.name AS country,
       totalPrefixes,
       ipv4Prefixes,
       ipv6Prefixes,
       CASE 
           WHEN totalPrefixes = 0 THEN 0 
           ELSE (toFloat(ipv6Prefixes) / totalPrefixes) * 100.0 
       END AS ipv6PrefixesPercentage
ORDER BY ipv6PrefixesPercentage DESC