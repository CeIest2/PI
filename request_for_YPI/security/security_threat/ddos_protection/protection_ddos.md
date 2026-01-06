### Analysis of the IRI Indicator

This indicator from the "Security" pillar evaluates a country's ability to withstand distributed denial-of-service (DDoS) attacks. A good score indicates that the country's critical infrastructures and services have protection mechanisms to absorb or filter malicious traffic, ensuring service continuity during an attack. The key technical entities are **Autonomous Systems (`:AS`)**, which can be both targets and vectors of protection, and more specifically **Content Delivery Networks (CDNs)**, which constitute a major first line of defense against large-scale DDoS attacks.

### YPI Relevance and Technical Analysis Plan

* **Relevance Assessment:** Case A (Relevant, via proxy analysis). The YPI schema does not contain an explicit "protection_ddos: true" property. However, this indicator can be effectively evaluated using **CDNs as a proxy**. The presence, reach, and use of CDN infrastructures in a country are strong technical indicators of its resilience to DDoS. A robust CDN ecosystem means that a significant portion of traffic is distributed and protected by default.

Here is the technical analysis plan for this indicator:

#### Query 1: Identify CDNs with a Local Presence

* **Query Objective:** The first step is to inventory the CDN networks operating directly in the country. The physical presence of these networks (via an AS registered in the country) is a sign of resilience, as it allows mitigation closer to the source and users, reducing latency and dependence on international links.

* **Cypher Query:**
    ```cypher
    // Lists AS categorized as CDN and located in a specific country.
    // The parameter $countryCode must be provided during execution (e.g., 'KE', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    // Uses bgp.tools tags to identify CDNs.
    MATCH (as)-[:CATEGORIZED]->(t:Tag {label: 'CDN'})
    // Retrieves the AS name for better readability.
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    RETURN as.asn AS cdnASN,
           n.name AS cdnName
    ORDER BY cdnName;
    ```

#### Query 2: Evaluate the Reach of CDNs Among the Population

* **Query Objective:** Knowing that a CDN is present is not enough; its importance must be measured. This query uses APNIC population data to estimate what percentage of the country's internet users is served by each local CDN. A CDN covering a large portion of the population provides a large-scale layer of protection.

* **Cypher Query:**
    ```cypher
    // Measures the percentage of a country's population served by CDN-type AS.
    // The parameter $countryCode must be provided during execution (e.g., 'KE', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
    MATCH (as)-[:CATEGORIZED]->(t:Tag {label: 'CDN'})
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    RETURN as.asn AS cdnASN,
           n.name AS cdnName,
           p.percent AS populationServedPercentage
    ORDER BY populationServedPercentage DESC;
    ```

#### Query 3: Verify the Protection of Popular Domains

* **Query Objective:** This query checks whether the most popular online services among the country's citizens (according to Cloudflare Radar) are effectively protected by CDN infrastructures (local or international). This allows moving from the availability of infrastructure to its effective use in protecting critical or high-traffic services.

* **Cypher Query:**
    ```cypher
    // Identifies popular domains in a country and checks if they are hosted by a CDN.
    // The parameter $countryCode must be provided during execution (e.g., 'KE', 'DE', 'BR').
    // Finds the most queried domains from the country.
    MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)
    WITH d, q.value AS queryPercentage ORDER BY queryPercentage DESC LIMIT 20
    // Finds the AS announcing the IP of these domains.
    MATCH (d)-[:RESOLVES_TO]->(:IP)-[:ORIGINATE]->(hostAS:AS)
    // Checks if this AS is a CDN.
    WHERE (hostAS)-[:CATEGORIZED]->(:Tag {label:"CDN"})
    OPTIONAL MATCH (hostAS)-[:NAME]->(n:Name)
    RETURN d.name AS popularDomain,
           hostAS.asn AS hostingCdnASN,
           n.name AS hostingCdnName,
           queryPercentage
    ORDER BY queryPercentage DESC;
    ```

### Overall Analysis Objective

* **Understanding:** These queries provide a multi-faceted view of a country's DDoS resilience. A poor score on the IRI "DDoS Protection" indicator could be explained by:
    1. A lack or very low number of CDNs operating locally (low result in **Query 1**).
    2. The CDNs present serve only a small fraction of the population, leaving the majority exposed (low result in **Query 2**).
    3. The country's most important sites and services do not leverage CDN solutions and are hosted on vulnerable infrastructures (low result in **Query 3**).
    Conversely, good results in these three queries would show a mature ecosystem where mitigation infrastructure is not only present and extensive but also actively used to protect essential services.

* **Improvement:** The results of this analysis point to concrete actions. If CDN presence is low, a national policy to attract major CDN players to establish points of presence (PoP) in local data centers (`:Facility`) would be a priority. If popular domains are not protected, awareness and incentive programs should be launched for local content providers, businesses, and government agencies to encourage the adoption of CDN solutions, thereby strengthening the overall security of the national digital ecosystem.