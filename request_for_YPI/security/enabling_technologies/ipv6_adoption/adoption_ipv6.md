### Analysis of the IRI Indicator

This indicator from the "Security" pillar is a high-level composite score, the Global Cybersecurity Index (GCI) of the International Telecommunication Union (ITU). It measures a country's commitment to cybersecurity based on five pillars: legal measures, technical measures, organizational measures, capacity building, and cooperation.

The "entities" involved are not discrete technical objects present in a network graph (such as AS or prefixes) but rather national concepts and structures (laws, cybersecurity agencies, training programs, etc.).

### YPI Relevance and Technical Analysis Plan

* **Relevance Assessment:** Case B (Not Relevant).

The Global Cybersecurity Index is a political and organizational measure derived from external sources (ITU) that are not modeled in the YPI schema. The YPI graph focuses on the technical topology and operational relationships of the Internet (BGP relationships, RPKI, IXP members, etc.). It does not contain any data related to political or legal index scores.

Therefore, it is impossible to create a Cypher query to directly query or analyze this indicator using the data available in YPI.

---

## Complementary Analyses (Routing Security and IPv6 Adoption)

Although the specific GCI indicator (a political score) is not modeled in YPI, other fundamental technical indicators related to routing security and IPv6 adoption can be analyzed.

---

### Query 1: Percentage of IPv6 Prefixes

* **Query Objective:** Calculate the percentage of BGP prefixes announced by AS in a country that are IPv6 prefixes (as opposed to IPv4). This provides a measure of IPv6 adoption at the routing level.

* **Cypher Query:**
    ```cypher
    // Calculates the percentage of AS in a country that announce IPv6 prefixes.
    // The parameter $countryCode must be provided during execution (e.g., 'KE', 'BE', 'CA').
    MATCH (c:Country {country_code: countryCode})
    
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
    ```

---

### Query 2: Identification of AS Without IPv6 Announcements

* **Query Objective:** Identify important AS (ranked by customer cone size) in a country that do not announce *any* IPv6 prefixes. This helps target IPv6 adoption efforts on the most impactful actors.

* **Cypher Query:**
    ```cypher
    // Identifies AS in a country without IPv6 announcements, ranked by importance.
    // The parameter $countryCode must be provided during execution (e.g., 'KE', 'BE', 'CA').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    
    // Check for the existence of IPv6 announcements for this AS.
    OPTIONAL MATCH (as)-[:ORIGINATE]->(p:Prefix)
    WHERE p.prefix CONTAINS ':'
    
    WITH as, count(p) AS ipv6PrefixCount
    // Keep only AS that have NO IPv6 announcements.
    WHERE ipv6PrefixCount = 0
    
    // Retrieve the rank and customer cone size to evaluate the importance of the AS.
    MATCH (as)-[r:RANK]->(rank:Ranking {name:'CAIDA ASRank'})
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    
    RETURN
        as.asn AS asn,
        n.name AS name,
        r['cone:numberAsns'] AS customerConeSize
    ORDER BY customerConeSize DESC
    LIMIT 15;
    ```