### IRI Indicator Analysis

This indicator, "Peering Efficiency," falls under the "Market Readiness" pillar. It measures the density of the local peering ecosystem by calculating the **ratio of networks (ASNs) participating in domestic Internet Exchange Points (IXPs) against the total number of networks in that country**. A high ratio indicates a mature and efficient market where a significant portion of local traffic can be exchanged directly within the country's borders, reducing reliance on international transit, lowering latency, and improving resilience.

The key technical entities involved are **:AS** (Autonomous Systems), **:IXP** (Internet Exchange Points), and the **:Country** they are associated with. The central relationship is **[:MEMBER_OF]** between an `:AS` and an `:IXP`.

---

### YPI Relevance and Technical Analysis Plan

* **Relevance Assessment:** Case A (Highly Relevant). The YPI schema, particularly with data from PeeringDB, is perfectly suited to analyze this indicator. It contains the necessary nodes (`:AS`, `:IXP`, `:Country`) and the critical relationship `(:AS)-[:MEMBER_OF]->(:IXP)` to directly calculate the ratio and explore the underlying structure of the peering ecosystem.

Here is the technical analysis plan for this indicator:

#### Query 1: Calculate the Core Peering Efficiency Ratio

* **Objective:** This query directly computes the metric described by the IRI indicator. It finds the total number of ASNs registered in a country and the number of those ASNs that are members of at least one IXP located within the same country. The ratio of these two numbers is the Peering Efficiency score.

* **Cypher Query:**
    ```cypher
    // Calculates the peering efficiency for a given country.
    // The $countryCode parameter must be provided at runtime (e.g., 'KE', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})

    // Get the total number of ASNs in the country.
    OPTIONAL MATCH (local_as:AS)-[:COUNTRY]->(c)
    WITH c, count(DISTINCT local_as) AS totalASNs

    // Get the number of local ASNs that are members of a local IXP.
    OPTIONAL MATCH (peering_as:AS)-[:COUNTRY]->(c)
    MATCH (peering_as)-[:MEMBER_OF]->(ixp:IXP)-[:COUNTRY]->(c)
    WITH totalASNs, count(DISTINCT peering_as) AS peeringASNs

    // Calculate the ratio. Avoid division by zero.
    RETURN
        totalASNs,
        peeringASNs,
        CASE
            WHEN totalASNs > 0 THEN toFloat(peeringASNs) / toFloat(totalASNs)
            ELSE 0
        END AS peeringEfficiencyRatio;
    ```

* **Expected Result Description:** The query returns a single row with three columns:
    * `totalASNs`: (Integer) The total count of distinct ASNs in the specified country.
    * `peeringASNs`: (Integer) The count of distinct local ASNs that peer at one or more local IXPs.
    * `peeringEfficiencyRatio`: (Float) The calculated efficiency score, from 0.0 to 1.0.

---

#### Query 2: List Domestic IXPs and their Peering Density

* **Objective:** To move beyond the single ratio and understand the distribution of the peering fabric. This query identifies all IXPs within the country and counts how many *local* ASNs are members of each one. This helps pinpoint the most critical IXPs and reveals if the ecosystem relies on a single IXP or is well-distributed.

* **Cypher Query:**
    ```cypher
    // Lists all IXPs in a country and counts their local members.
    // The $countryCode parameter must be provided at runtime (e.g., 'KE', 'DE', 'BR').
    MATCH (ixp:IXP)-[:COUNTRY]->(:Country {country_code: $countryCode})
    
    // Count local ASNs connected to this IXP.
    OPTIONAL MATCH (local_as:AS)-[:COUNTRY]->(:Country {country_code: $countryCode})
    MATCH (local_as)-[:MEMBER_OF]->(ixp)
    
    WITH ixp, count(DISTINCT local_as) as localMemberCount
    OPTIONAL MATCH (ixp)-[:NAME]->(n:Name)
    
    RETURN
        ixp.ix_id AS ixpId,
        n.name AS ixpName,
        localMemberCount
    ORDER BY localMemberCount DESC;
    ```

* **Expected Result Description:** The query returns a list of IXPs in the country, with each row containing:
    * `ixpId`: (Integer) The unique identifier of the IXP from PeeringDB.
    * `ixpName`: (String) The common name of the IXP.
    * `localMemberCount`: (Integer) The number of ASNs from the same country that are members of this IXP.

---

#### Query 3: Identify High-Impact ASNs Not Peering Domestically

* **Objective:** To identify which networks are missing from the domestic peering ecosystem. A low efficiency score is often due to a few large networks opting out. This query finds ASNs in the country that are *not* members of any local IXP and ranks them by their CAIDA AS Rank cone size, highlighting the most significant networks whose participation could dramatically improve the country's peering efficiency.

* **Cypher Query:**
    ```cypher
    // Finds important local ASNs that do not peer at any local IXP.
    // The $countryCode parameter must be provided at runtime (e.g., 'KE', 'DE', 'BR').
    MATCH (c:Country {country_code: $countryCode})
    MATCH (local_as:AS)-[:COUNTRY]->(c)
    
    // Ensure the AS is NOT a member of any IXP in the same country.
    WHERE NOT EXISTS {
      MATCH (local_as)-[:MEMBER_OF]->(:IXP)-[:COUNTRY]->(c)
    }
    
    // Get CAIDA AS Rank data to measure the AS's importance (customer cone size).
    OPTIONAL MATCH (local_as)-[r:RANK]->(:Ranking {name:'CAIDA ASRank'})
    OPTIONAL MATCH (local_as)-[:NAME]->(n:Name)
    
    RETURN
        local_as.asn AS asn,
        n.name AS asName,
        r['cone:numberAsns'] AS customerConeSize
    ORDER BY customerConeSize DESC
    LIMIT 20;
    ```

* **Expected Result Description:** The query returns a list of the top 20 most impactful non-peering ASNs, with each row containing:
    * `asn`: (Integer) The Autonomous System Number.
    * `asName`: (String) The name of the organization owning the AS.
    * `customerConeSize`: (Integer) The number of ASNs in this AS's customer cone, indicating its importance in the downstream market.

---

#### Query 4 (Temporal Analysis): Track the Growth Momentum of the Peering Ecosystem

* **Objective:** This query analyzes the dynamism of the peering ecosystem by measuring its growth rate. Instead of looking at the total number of members at a point in time, it counts how many new ASNs join a domestic IXP for the very first time each year. This provides a powerful view of the ecosystem's momentum and the effectiveness of community-building or policy efforts.

* **Cypher Query:**
    ```cypher
    // Tracks the number of new ASNs joining a local IXP for the first time each year.
    // The $countryCode parameter must be provided at execution.
    // PREREQUISITE: The :MEMBER_OF relationship must have a temporal property (e.g., .timestamp in ms).
    MATCH (c:Country {country_code: $countryCode})
    MATCH (as:AS)-[:COUNTRY]->(c)
    MATCH (ixp:IXP)-[:COUNTRY]->(c)
    MATCH (as)-[r:MEMBER_OF]->(ixp)
    WHERE r.timestamp IS NOT NULL

    // For each AS, find its earliest join date across all local IXPs.
    WITH as, min(r.timestamp) AS firstJoinTimestamp

    // Group by the year of that first join date.
    WITH datetime({epochMillis: firstJoinTimestamp}).year AS joinYear

    RETURN
        joinYear,
        count(*) AS newPeerAsnsCount
    ORDER BY joinYear ASC;
    ```

* **Expected Result Description:** The query returns a list of years and the corresponding count of "new entrants" to the peering scene for that year. Each row contains:
    * `joinYear`: (Integer) The year in which one or more ASNs first joined a local IXP.
    * `newPeerAsnsCount`: (Integer) The number of ASNs that joined for the first time in that year.

---

### Overall Goal of the Analysis (Understanding & Improvement)

* **Understanding:** Executing this full set of queries provides a multi-dimensional view of a country's peering health. **Query 1** delivers the headline score ("what"). **Query 2** maps the domestic infrastructure ("where"). **Query 3** identifies the key missing players ("who"). Finally, **Query 4** reveals the ecosystem's trajectory and momentum ("when" and "how fast"). Together, they allow us to distinguish between a country with a mature, saturated peering market (high ratio, low recent growth) and one that is immature but rapidly improving (low ratio, high recent growth).

* **Improvement:** The results directly inform strategic action.
    * If **Query 1** shows a low ratio and **Query 2** shows few active IXPs, the priority is to foster the creation of a national IXP.
    * If **Query 2** shows healthy IXPs but **Query 3** lists influential ASNs, the action is targeted advocacy to encourage these specific networks to peer locally.
    * The trend from **Query 4** is crucial for evaluating policy. A flat or declining number of new joiners is a strong signal that new incentives are needed. Conversely, a strong upward trend justifies continued investment in the programs that are fostering this growth.