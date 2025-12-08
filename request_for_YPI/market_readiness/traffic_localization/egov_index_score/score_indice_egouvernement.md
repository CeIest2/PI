### IRI Indicator Analysis: E-Government Development Index Score

This indicator from the "Market Readiness" pillar measures the maturity of a country's digital public services, based on the United Nations EGDI. A high score indicates a strong presence and high quality of online services for citizens. The key underlying technical entities are `:DomainName` (government portals) and the `:AS` and `:Prefix` that host these services.

### YPI Relevance and Technical Analysis Plan

* **Relevance Assessment:** Case A (Relevant, with nuance). The YPI does not contain the EGDI score itself, as it is an external composite indicator. However, the YPI is **extremely relevant** for analyzing the **technical infrastructure underpinning these government services**. We can use it to assess the resilience, localization, and security of e-government portal hosting, which directly influences the availability and performance of these services.

The plan consists of first identifying potential government domains, and then deeply analyzing their hosting infrastructure.

#### Query 1: Discover potential government domains by local popularity

* **Query Objective:** E-government services are often among the most visited sites from within a country. This query identifies the most popular domains ending with the country's ccTLD, based on the percentage of DNS queries originating from that same country. This is an excellent starting point for spotting major national portals.

* **Cypher Query:**
    ```cypher
    // Finds popular domains under a country's ccTLD, sorted by % of local queries.
    // The $countryCode parameter must be provided at execution (e.g., 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})
    MATCH (d:DomainName)-[q:QUERIED_FROM]->(c)
    // Filters for domains ending with the country's ccTLD (e.g., '.sn')
    WHERE d.name ENDS WITH '.' + toLower($countryCode)
    // Uses Tranco rank as a secondary sort criterion
    OPTIONAL MATCH (d)-[r:RANK]->(:Ranking {name:"Tranco top 1M"})
    RETURN d.name AS domainName,
           q.value AS percentageOfLocalQueries,
           r.rank AS trancoRank
    ORDER BY percentageOfLocalQueries DESC, trancoRank ASC
    LIMIT 25;
    ```

#### Query 2: Analyze the hosting infrastructure of a specific domain

* **Query Objective:** Once a government domain is identified (via Query 1 or local knowledge), this query maps its hosting infrastructure. It determines which Autonomous System(s) (AS) host the domain and, crucially, whether this hosting is local (in-country) or foreign. This is fundamental for assessing digital sovereignty and reliance on external infrastructure.

* **Cypher Query:**
    ```cypher
    // Analyzes the hosting infrastructure for a given domain name.
    // PARAMETERS: $domainName (e.g., 'service-public.fr'), $countryCode (e.g., 'FR').
    MATCH (d:DomainName {name: $domainName})
    // Finds the IPs to which the domain resolves
    MATCH (d)-[:RESOLVES_TO]->(ip:IP)
    // Finds the prefix and the originating AS
    MATCH (p:Prefix)-[:HAS_IP]->(ip)
    MATCH (hostingAS:AS)-[:ORIGINATE]->(p)
    // Retrieves hosting AS info (name, country)
    OPTIONAL MATCH (hostingAS)-[:NAME]->(n:Name)
    OPTIONAL MATCH (hostingAS)-[:COUNTRY]->(hostingCountry:Country)
    RETURN DISTINCT
           hostingAS.asn AS hostingASN,
           n.name AS hostingASName,
           hostingCountry.country_code AS hostingASCountry,
           // Compares the AS country to the analyzed country
           (hostingCountry.country_code = $countryCode) AS isHostedLocally
    LIMIT 10;
    ```

#### Query 3: Assess routing security of e-government infrastructure

* **Query Objective:** This query evaluates the routing security posture of the ASes hosting government services. By checking the RPKI (Resource Public Key Infrastructure) status of IP prefixes announced by these ASes, we can determine if the infrastructure is protected against BGP hijacking, an attack that could render e-government services inaccessible.

* **Cypher Query:**
    ```cypher
    // Checks the RPKI status of prefixes announced by an AS hosting a government service.
    // PARAMETER: $hostingASN (an ASN identified with the previous query, e.g., 16276)
    MATCH (hostingAS:AS {asn: $hostingASN})-[:ORIGINATE]->(p:Prefix)
    MATCH (p)-[:CATEGORIZED]->(t:Tag)
    WHERE t.label STARTS WITH 'RPKI'
    RETURN t.label AS rpkiStatus,
           count(p) AS numberOfPrefixes
    ORDER BY numberOfPrefixes DESC;
    ```

### Global Analysis Objective

Executing these queries will provide an X-ray of a country's e-government technical infrastructure.

* **Understanding:** The results will tell us if the government's digital strategy relies on national infrastructure or is outsourced to international hosts and clouds. A high EGDI score but with entirely foreign hosting highlights a strong dependency. A low score might be explained by hosting on a small number of local ASes with poor routing security (many `RPKI NotFound` or `Invalid` prefixes), constituting a significant technical risk to public service continuity.

* **Improvement:** If the analysis reveals that critical portals are hosted on local ASes without good routing hygiene (low RPKI/MANRS adoption), a clear corrective action is to work with government agencies to require security standards from their providers. If all services are hosted abroad, this can initiate a strategic discussion on the importance of developing a government or sovereign cloud to strengthen national resilience and maintain control over citizen data.