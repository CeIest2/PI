### Analysis of the IRI Indicator

This indicator, located in the "Security" pillar and the "Routing Hygiene" sub-pillar, aims to evaluate the robustness of a country's connections to the rest of the Internet. It measures how and with what quality the networks (Autonomous Systems - AS) of a country are connected to their Internet transit providers, also called "upstream" providers. A good score suggests that local networks have numerous and high-quality connections to the rest of the Internet, reducing the risk of isolation in the event of a major provider failure. The key technical entities are the `:AS` of the target country, the `:AS` acting as their providers, and the relationships that connect them.

### YPI Relevance and Technical Analysis Plan

* **Relevance Assessment:** Case A (Highly Relevant). The YPI schema is ideal for this analysis. It not only contains transit relationships (provider-to-customer) via BGPKIT but also CAIDA ranking data (AS Rank), which is the reference source for this IRI indicator. We can therefore identify both the connections and evaluate their quality.

Here is the technical analysis plan for this indicator:

#### Query 1: Identify Upstream Providers and Evaluate Their Quality

* **Query Objective:** This query provides a complete inventory of transit providers for a given country. For each provider, it counts the number of local client networks it serves and, most importantly, retrieves its global ranking according to CAIDA (AS Rank). A low rank (close to 1) indicates a major provider at the core of the Internet. This query allows visualization of both the quantity and intrinsic quality of the country's upstream connections.

* **Cypher Query:**
    ```cypher
    // Identifies the transit providers of a country, counts their local clients, and displays their CAIDA rank.
    // The parameter $countryCode must be provided during execution (e.g., 'NG', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(local_as:AS)
    // Finds the provider-to-customer relationship (rel=1) via BGPKIT data.
    MATCH (local_as)-[:PEERS_WITH {rel: 1}]->(provider:AS)
    // Ensures the provider is external to the country.
    WHERE NOT (provider)-[:COUNTRY]->(c)
    // Retrieves the CAIDA ranking of the provider.
    WITH provider, count(DISTINCT local_as) AS local_clients
    OPTIONAL MATCH (provider)-[r:RANK]->(rank_node:Ranking {name: 'CAIDA ASRank'})
    OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
    RETURN provider.asn AS providerASN,
           n.name AS providerName,
           local_clients,
           r.rank AS caidaASRank
    ORDER BY caidaASRank ASC, local_clients DESC
    LIMIT 20;
    ```

#### Query 2: Analyze the Qualitative Distribution of the Transit Portfolio

* **Query Objective:** Instead of simply listing providers, this query analyzes the country's transit portfolio by aggregating providers into "tiers" of quality based on their CAIDA rank. It answers the question: "Is the country primarily connected to the global elite (Top 100), major international operators (Top 500), or more regional players?" A strong concentration in the upper tiers is a sign of high resilience.

* **Cypher Query:**
    ```cypher
    // Analyzes the distribution of a country's transit providers by CAIDA rank category.
    // The parameter $countryCode must be provided during execution (e.g., 'NG', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(local_as:AS)
    MATCH (local_as)-[:PEERS_WITH {rel: 1}]->(provider:AS)
    WHERE NOT (provider)-[:COUNTRY]->(c)
    // Retrieves the CAIDA ranking of each unique provider.
    WITH DISTINCT provider
    MATCH (provider)-[r:RANK]->(rank_node:Ranking {name: 'CAIDA ASRank'})
    // Categorizes each provider based on its rank.
    WITH provider, r.rank AS rank
    WITH CASE
        WHEN rank <= 100 THEN 'A) Top 100 (Internet Core)'
        WHEN rank > 100 AND rank <= 500 THEN 'B) Top 101-500 (Major)'
        WHEN rank > 500 AND rank <= 2000 THEN 'C) Top 501-2000 (Important)'
        ELSE 'D) Beyond 2000 (Regional/Niche)'
    END AS providerTier
    // Counts the number of providers in each category.
    RETURN providerTier,
           count(provider) AS numberOfProviders
    ORDER BY providerTier ASC;
    ```

#### Query 3: Concentration of Upstream Providers

* **Query Objective:** This query identifies the main points of concentration for external peering. It looks for foreign AS (peers) that are connected to the largest number of domestic AS. A high number of clients for a single external peer may indicate strong dependency.

* **Cypher Query:**
    ```cypher
    // Concentration of upstream providers
    
    // Finds the country's AS and their external peers
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as_fr:AS)
    MATCH (as_fr)-[:PEERS_WITH]-(peer:AS)
    MATCH (peer)-[:COUNTRY]->(peer_country:Country)
    WHERE peer_country <> c
    
    // Groups by external peer and counts connected domestic AS
    RETURN peer.asn AS upstreamAS, 
           peer_country.country_code AS upstreamCountry,
           count(DISTINCT as_fr) AS connectedDomesticClients
    ORDER BY connectedDomesticClients DESC
    LIMIT 10
    ```

---

### Query 4: Diversity of Upstream Peers

* **Query Objective:** This query evaluates the overall diversity of external connections. It counts the total number of domestic AS and compares it to the total number of unique external peers they are connected to. A high ratio of peers per domestic operator suggests rich and diverse connectivity.

* **Cypher Query:**
    ```cypher
    // Diversity of upstream peers
    
    // Finds the country and its AS
    MATCH (c:Country {country_code: $countryCode})
    MATCH (c)<-[:COUNTRY]-(as_fr:AS)
    
    // Finds all peers of these AS
    MATCH (as_fr)-[:PEERS_WITH]-(peer:AS)
    
    // Finds the country of these peers
    MATCH (peer)-[:COUNTRY]->(peer_country:Country)
    
    // Filters to keep only EXTERNAL peers
    WHERE peer_country <> c
    
    // Counts domestic AS and unique external peers
    RETURN c.name AS country,
           count(DISTINCT as_fr) AS domesticOperators,
           count(DISTINCT peer) AS uniqueExternalPeers
    ORDER BY uniqueExternalPeers DESC
    ```

---

### Query 5: Presence in International IXPs

* **Query Objective:** This query measures the involvement of a country's operators in Internet Exchange Points (IXPs) located abroad. Connecting to international IXPs is a key strategy to diversify connectivity, reduce transit costs, and improve latency to foreign networks.

* **Cypher Query:**
    ```cypher
    // Presence in international IXPs
    
    // Finds the country and its AS
    MATCH (c:Country {country_code: $countryCode})
    MATCH (c)<-[:COUNTRY]-(as_fr:AS)
    
    // Finds the IXPs they are members of
    MATCH (as_fr)-[:MEMBER_OF]->(ixp:IXP)
    
    // Finds the country of the IXP
    MATCH (ixp)-[:COUNTRY]->(ixp_country:Country)
    
    // Filters to keep only IXPs abroad
    WHERE ixp_country <> c
    
    // Counts
    RETURN c.name AS country,
           count(DISTINCT ixp) AS uniqueInternationalIXPs,
           count(DISTINCT as_fr) AS connectedInternationalOperators
    ORDER BY connectedInternationalOperators DESC
    ```

### Overall Analysis Objective

Executing these queries will provide a clear and detailed picture of the country's upstream connectivity, directly explaining its IRI score for this indicator.

* **Understanding:** If the country's IRI score is good, we expect **Query 1** to return a diverse list of providers with very low CAIDA ranks (many AS in the top 100). **Query 2** will confirm this by showing a high number of providers in the "A) Top 100" category. Conversely, a poor score will result in a short list in Query 1, potentially dominated by providers with high CAIDA ranks, and Query 2 will show a concentration of providers in the "C)" or "D)" categories, indicating reliance on second- or third-tier players.

* **Improvement:** The results are directly actionable. If the analysis reveals weak connectivity to the Internet core providers (few or no providers in the "A" category), a strategic action would be to develop public policies to attract major global transit operators to establish a point of presence (PoP) in the country. This could involve creating carrier-neutral data centers or tax incentives to facilitate direct, more efficient, and resilient connections for local AS to the global Internet core.