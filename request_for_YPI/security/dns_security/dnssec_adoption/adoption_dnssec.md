### Analysis of the IRI Indicator

This indicator from the "Security" pillar measures the deployment of Domain Name System Security Extensions (DNSSEC). The goal of DNSSEC is to ensure the authenticity and integrity of DNS responses by adding cryptographic signatures. A high adoption rate means that domain names relevant to the country are protected against attacks such as DNS cache poisoning or spoofing. The key technical entities are `:DomainName`, `:AS`, and `:Country`.

### YPI Relevance and Technical Analysis Plan

* **Relevance Assessment:** Case A (Partially Relevant). The YPI schema does not contain a direct property indicating whether a domain is signed with DNSSEC. Therefore, YPI cannot *directly* calculate an adoption score. However, YPI is highly relevant for a two-step analysis: it can first identify the most critical and relevant domains for a given country. These domain lists can then be analyzed with an external tool to verify their DNSSEC status. The following queries are used to generate these target lists.

Here is the technical analysis plan for this indicator:

#### Query 1: Identify the most popular domains queried from the country

* **Query Objective:** This query identifies the domain names most frequently resolved by users within the target country, using data from Cloudflare Radar. Protecting these domains is the most critical for the security of the country's internet users, as these are the services they use the most. Low DNSSEC adoption on this list exposes a large portion of the population to risks.

* **Cypher Query:**
    ```cypher
    // Retrieves the 25 most popular domains for a given country, based on the percentage of DNS queries.
    // The parameter $countryCode must be provided during execution (e.g., 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[q:QUERIED_FROM]-(d:DomainName)
    RETURN d.name AS domainName,
           q.value AS queryPercentage
    ORDER BY queryPercentage DESC
    LIMIT 25;
    ```

#### Query 2: Identify popular domains hosted in the country

* **Query Objective:** This query identifies popular domains (ranked by Tranco) that are hosted locally, i.e., whose IP addresses are announced by autonomous systems (AS) located in the country. This list represents the local content ecosystem (government, businesses, media). The DNSSEC status of these domains is an excellent indicator of the maturity of national content providers in terms of security.

* **Cypher Query:**
    ```cypher
    // Retrieves domains from the Tranco top 1M resolved to IPs hosted in the target country.
    // The parameter $countryCode must be provided during execution (e.g., 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)<-[:ORIGINATE]-(:Prefix)<-[:MEMBER_OF]-(:IP)<-[:RESOLVES_TO]-(d:DomainName)
    // Uses the Tranco ranking to filter by popularity
    MATCH (d)-[r:RANK]->(rk:Ranking)
    WHERE rk.name CONTAINS 'Tranco'
    RETURN d.name AS domainName,
           r.rank AS popularityRank,
           as.asn AS hostingASN
    ORDER BY r.rank ASC
    LIMIT 25;
    ```

### Overall Analysis Objective

Executing these two queries will not provide the DNSSEC adoption score but will provide the essential data to contextualize and act.

* **Understanding:** The two domain lists (the most *queried* and the most *hosted*) constitute the most relevant sample for the country. Once these lists are exported and analyzed with an external tool (e.g., via `dig +dnssec` scripts), we can precisely understand *why* the IRI score is good or bad. A poor score would be explained by the absence of signatures on government domains (`.gov.xx`), major banking sites, media, or the most-used international services by the population.

* **Improvement:** These lists constitute a concrete action plan. If locally hosted domains (Query 2) are not signed, the national cybersecurity agency or the ccTLD registry can launch an awareness and training campaign targeted at the owners of these domains. If popular international domains (Query 1) are not signed, the effort should focus on promoting **DNSSEC validation** at the level of local internet service providers to protect users even if the remote domain is not secured.