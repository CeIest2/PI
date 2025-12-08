### IRI Indicator Analysis

This indicator from the "Market Readiness" pillar measures the vitality of the local content ecosystem based on the number of domains registered with the country's ccTLD (country-code Top-Level Domain), such as `.sn` for Senegal or `.jp` for Japan. A high number of domains suggests strong production and consumption of local services and content, which is a sign of digital maturity and resilience. The key technical entities are `:DomainName` and their implicit link to a `:Country` via their suffix.

### YPI Relevance and Technical Analysis Plan

* **Relevance Assessment:** Case A (Highly Relevant). Although YPI does not contain the exhaustive list of *all* registered domains (the IRI source is DomainTools), it contains crucial information on the most *popular* and most *queried* domains (via Tranco, Cloudflare Radar) and where their content is hosted. This analysis verifies whether the theoretical existence of ccTLD domains translates into actual local consumption and hosting, which is at the heart of resilience.

Here is the technical analysis plan for this indicator:

#### Query 1: Popularity of ccTLD domains within the country

* **Query Objective:** This query verifies whether national ccTLD domains are actually popular among users in the country. A high IRI score for "Number of domains" is much more significant if these domains are actively accessed locally. This measures the match between local content supply (ccTLD domains) and local demand.

* **Cypher Query:**
    ```cypher
    // Identifies the most queried ccTLD domains from within the country.
    // The $countryCode parameter must be provided at execution (e.g., 'SN', 'FR', 'JP').
    MATCH (c:Country {country_code: $countryCode})
    // Filters domains ending with the country's ccTLD (e.g., .sn)
    MATCH (d:DomainName)
    WHERE d.name ENDS WITH '.' + toLower($countryCode)

    // Finds the query relationship from this country (source: Cloudflare Radar)
    MATCH (d)-[q:QUERIED_FROM]->(c)
    WHERE q.value IS NOT NULL

    RETURN d.name AS localDomain,
           q.value AS percentageOfQueriesInCountry
    ORDER BY percentageOfQueriesInCountry DESC
    LIMIT 20;
    ```

#### Query 2: Hosting location of popular ccTLD domains

* **Query Objective:** This query is essential for resilience. It determines whether the content of popular ccTLD domains is hosted locally or abroad. If a large number of `.sn` domains are hosted in Europe or the US, local traffic must make international round trips, which increases latency and dependency on external infrastructure (submarine cables, international transit).

* **Cypher Query:**
    ```cypher
    // Analyzes the geographic distribution of hosting for the top 100 popular ccTLD domains.
    // The $countryCode parameter must be provided at execution (e.g., 'SN', 'FR', 'JP').
    MATCH (d:DomainName)
    WHERE d.name ENDS WITH '.' + toLower($countryCode)

    // Focuses on popular domains (source: Tranco) for relevant analysis
    MATCH (d)-[r:RANK]->(:Ranking {name:"Tranco top 1M"})
    WITH d ORDER BY r.rank LIMIT 100

    // Finds the country of the AS announcing the prefix containing the domain's IP
    MATCH (d)-[:RESOLVES_TO]->(:IP)<-[:ORIGINATE]-(hostingAS:AS)
    MATCH (hostingAS)-[:COUNTRY]->(hostingCountry:Country)

    WITH hostingCountry, count(DISTINCT d) AS domainCount
    RETURN hostingCountry.country_code AS hostingCountryCode,
           domainCount
    ORDER BY domainCount DESC;
    ```

### Global Analysis Objective

Executing these queries will provide a clear picture of traffic and content localization for a given country.

* **Understanding:** If **Query 1** shows low popularity of ccTLD domains, it means that even if many domains are registered, they do not constitute the core of the country's digital consumption. If **Query 2** reveals that a majority of popular ccTLD domains are hosted abroad (a `hostingCountryCode` different from the analyzed `$countryCode`), this highlights "content leakage" and critical infrastructural dependency. A good IRI score on this indicator should correlate with popular ccTLD domains (Query 1) that are mostly hosted locally (Query 2).

* **Improvement:** If results show predominantly foreign hosting, a concrete action would be to develop the local ecosystem of data centers and hosting services. Incentive policies (subsidies, training) could encourage local companies and content creators to repatriate their services. If the problem is the low popularity of local domains, efforts should focus on promoting local content and developing digital services relevant to the population.