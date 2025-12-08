### IRI Indicator Analysis

This indicator from the **"Market Readiness"** pillar evaluates a country's reliance on upstream Internet transit providers. A low score suggests a high dependency on a small number of providers, constituting a Single Point of Failure risk and low resilience. The key technical entities are the `:AS` located within the country and the `:AS` (often foreign) that provide them with transit.

### YPI Relevance and Technical Analysis Plan

* **Relevance Assessment:** Case A (Highly Relevant) ✅. The YPI schema contains BGP topology data (via BGPKIT) and quantified dependency data (via IHR) that allow for an in-depth analysis of this indicator.

Here is the technical analysis plan for this indicator:

#### Query 1: Identify upstream transit providers by customer count

* **Query Objective:** This query is the fundamental first step. It uses BGP relationships to identify all external transit providers for the target country's networks (AS). The goal is to count how many local ASes depend on each provider, thus revealing the most critical players in the transit market for that country in terms of market share.

* **Cypher Query:**
    ```cypher
    // Identifies transit providers for a given country and counts their local customers.
    // The $countryCode parameter must be provided at execution (e.g., 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    // Uses BGPKIT (r.rel=1) to find Provider-to-Customer relationships.
    MATCH (as)-[r:PEERS_WITH {rel: 1}]->(provider:AS)
    // Ensures the provider is not itself local (focus on international transit).
    WHERE NOT (provider)-[:COUNTRY]->(c)
    WITH provider, count(DISTINCT as) AS localCustomers
    // Retrieves the provider name for better readability.
    OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
    RETURN provider.asn AS providerASN,
           n.name AS providerName,
           localCustomers
    ORDER BY localCustomers DESC
    LIMIT 10;
    ```

#### Query 2: Analyze dependency strength (Hegemony)

* **Query Objective:** While the first query counts customers, this one quantifies the **strength** of the dependency using the IHR hegemony metric (`d.hege`). A high hegemony score indicates critical dependency. This query helps distinguish a provider with many small customers from a provider upon whom the country's most important networks depend.

* **Cypher Query:**
    ```cypher
    // Measures the average dependency of a country's ASes on their transit providers.
    // The $countryCode parameter must be provided at execution (e.g., 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})<-[:COUNTRY]-(as:AS)
    // Uses the dependency relationship and the IHR hegemony metric.
    MATCH (as)-[d:DEPENDS_ON]->(provider:AS)
    // Filters for significant dependencies to reduce noise.
    WHERE d.hege > 0.1 AND NOT (provider)-[:COUNTRY]->(c)
    WITH provider, avg(d.hege) AS averageHegemony, count(DISTINCT as) AS dependentASNs
    OPTIONAL MATCH (provider)-[:NAME]->(n:Name)
    RETURN provider.asn AS providerASN,
           n.name AS providerName,
           averageHegemony,
           dependentASNs
    ORDER BY averageHegemony DESC, dependentASNs DESC
    LIMIT 10;
    ```

### Global Analysis Objective (Understanding and Improvement)

Executing these two queries for a given country will provide a precise technical view of its transit diversity.

* **Understanding 🧐:** **Query 1** will identify dominant providers in terms of customer count. **Query 2** will confirm if this dominance translates into critical technical dependency (high hegemony). If the same `providerASN` appears at the top of both lists with high scores, this materializes the theoretical risk measured by the IRI. We will have identified a single point of failure or a transit oligopoly.

* **Improvement 💡:** Armed with this data, a concrete action would be to launch a diversification program. This could include subsidies or training to encourage local ASes to connect to other transit providers (Tier-1/Tier-2). More strategically, this could motivate the strengthening of the local peering ecosystem (see the "Peering Efficiency" indicator) so that local traffic remains local and does not depend on these international transit providers.