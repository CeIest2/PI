# HTTPS Adoption — Query Explanation

## What is "HTTPS adoption" (metric)
HTTPS adoption (in this context) measures the share of observed hostnames for a given scope (here: a country) that serve content via HTTPS (their recorded origin string starts with `https`). It is expressed as a percentage:
- 100% means all observed hostnames are served over HTTPS.
- 0% means none of the observed hostnames use HTTPS.
This metric is commonly used to evaluate how widely encrypted transport is deployed across the web footprint of a country, organization, or domain set.

## 1st query
This Cypher query computes the HTTPS adoption rate among hostnames associated with a given country (identified by `$countryCode`) according to a Google-derived ranking dataset stored in Neo4j. It returns three values:
- `https_adoption_rate` — percentage of distinct hostnames served over HTTPS,
- `count_https` — number of distinct hostnames whose origin begins with `https`,
- `count_total` — total number of distinct hostnames considered.
- Security indicator: HTTPS adoption is a primary signal of basic transport-layer security and confidentiality for web traffic.
- Policy & monitoring: Helps policymakers and network operators track progress on secure-by-default goals and measure the impact of initiatives promoting HTTPS.
- Comparability: Using a consistent ranking source (Google in this dataset) and de-duplicating hostnames gives a repeatable baseline for cross-country or over-time comparisons.
- Actionable counts: Returning `count_https` and `count_total` alongside the percentage lets analysts understand sample sizes and decide whether the metric is statistically meaningful for the country.




