### IRI Indicator Analysis

This indicator, located in the "Market Readiness" pillar, measures the level of internet access market concentration in a country. It uses the Herfindahl-Hirschman Index (HHI), which is an accepted measure of competition. A low score on this IRI indicator suggests a market dominated by one or a few players (monopoly/oligopoly), which harms resilience by creating excessive dependencies and limiting consumer choice. The key technical entities are **Autonomous Systems (`:AS`)** acting as access providers, and their respective market share, which IRI and YPI estimate via the served population.

### YPI Relevance and Technical Analysis Plan

* **Relevance Assessment:** Case A (Highly Relevant). The YPI schema directly integrates "Population Estimates" data from APNIC, the source cited by the IRI. The relationship `(:AS)-[:POPULATION]->(:Country)` contains a property representing the percentage of a country's population served by an AS, which is an excellent proxy for market share.

Here is the technical analysis plan for this indicator:

#### Query 1: List the market share (population served) of ASes in a country

* **Query Objective:** This fundamental query establishes the market structure. It identifies all access providers (AS) operating in the target country and returns their estimated market share. This allows immediate visualization of who the dominant players are and the fragmentation of the market.

* **Cypher Query:**
    ```cypher
    // Retrieves the market share of each AS in a given country.
    // The $countryCode parameter must be provided at execution (e.g., 'CI' for Ivory Coast).
    MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
    // Retrieves the AS name for better readability.
    OPTIONAL MATCH (as)-[:NAME]->(n:Name)
    RETURN as.asn AS asn,
           n.name AS asName,
           p.percent AS marketSharePercent
    ORDER BY marketSharePercent DESC;
    ```

#### Query 2: Directly calculate the Market Concentration Index (HHI)

* **Query Objective:** This query goes beyond a simple list by directly calculating the HHI, thus replicating the IRI methodology. The index is calculated by summing the squares of the market shares of each provider. A high result (close to 10,000) indicates a monopoly, while a low result (below 1,500) suggests a competitive market.

* **Cypher Query:**
    ```cypher
    // Calculates the Herfindahl-Hirschman Index (HHI) for a given country.
    // The $countryCode parameter must be provided at execution (e.g., 'CI').
    MATCH (c:Country {country_code: $countryCode})<-[p:POPULATION]-(as:AS)
    // Calculates the sum of squares of market shares (in percentage).
    WITH sum(p.percent^2) AS hhi
    RETURN hhi,
        CASE
            WHEN hhi < 1500 THEN 'Competitive Market'
            WHEN hhi >= 1500 AND hhi <= 2500 THEN 'Moderately Concentrated Market'
            ELSE 'Highly Concentrated Market'
        END AS marketConcentration;
    ```

### Global Analysis Objective

Executing these queries will provide a quantitative and unambiguous view of competition in a country's internet market.

* **Understanding:** If a country has a poor IRI score for "Market Competition," **Query 1** will immediately identify the one or few ASes dominating the market. **Query 2** will confirm this observation with a high HHI score, thus technically explaining the resilience weakness on this point. We are not just satisfied knowing the score is bad; we know *who* the dominant players are and in what proportion.

* **Improvement:** Armed with this data, it is possible to initiate targeted actions. If the analysis reveals a high HHI, this constitutes solid evidence to present to national regulators to argue for pro-competitive policies. These policies could include measures to facilitate the entry of new players, ensure fair access to essential infrastructure (fiber, towers), or examine the business practices of dominant operators. The goal is to decrease concentration to increase resilience, quality of service, and affordability for end-users.