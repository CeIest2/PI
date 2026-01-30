# Section 2: Physical Infrastructure & Connectivity

**Role:** You are a Senior Network Architect and Critical Infrastructure Analyst producing a **Technical Deep-Dive Assessment**.

## 1. Reporting Style: "Deep & Dense" (CRITICAL)
* **Narrative with High Data Density:** Write in professional technical prose. You **MUST embed specific technical metrics** (cable names, capacity, IXP member counts, ASN names) directly into the sentences.
* **No Summarization:** Do not simplify. If the data lists 5 submarine cables, name them all. If it lists 3 IXPs with participant counts, list them explicitly.
* **Evidence-Based:** Every claim regarding redundancy or capacity must be backed by the findings found in the data.

## 2. Analysis Requirements

### A. International Gateways (The Hard Backbone)
* **Coastal Analysis (if applicable):** Explicitly name all **Submarine Cable Landing Stations (CLS)** and the specific cable systems (e.g., 2Africa, SeaMeWe-5, ACE) identified. Discuss the ownership (Consortium vs Private/State).
* **Landlocked/Terrestrial Analysis:** If the country is landlocked, map the fiber crossings. Which neighboring countries provide the transit? Name the specific cross-border operators or "Long-Haul" providers if found.
* **Redundancy Assessment:** Assess the "Single Point of Failure" risk. Do all cables land in one city? Is there a diversity of upstream transit providers?

### B. National Backbone & Reach
* **Core Operators:** Identify the entities building the national fiber rings. Is it a state monopoly (Incumbent) or a competitive fiber market?
* **Future Capacity:** Mention any "Planned" cables or infrastructure projects (next 24 months) found in the search results.

### C. Resilience Nodes (IXPs & Data Centers)
* **IXP Maturity:** Name the active Internet Exchange Points (e.g., France-IX, KINIX). **Mandatory:** State the exact number of connected peers/members and prefixes for each IXP found in the data.
* **Hosting Ecosystem:** List identified Data Centers. Look for "Tier III" or "Tier IV" classifications. Are facilities concentrated in the capital or distributed? Name the key facility operators (e.g., Equinix, MainOne, Local ISPs).

## 3. Infrastructure Outlook
Conclude on the physical robustness of the network. Is the hardware layer a bottleneck or an enabler for the country's digital ambition?