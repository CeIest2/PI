# Section 2: Physical Infrastructure & Connectivity

**Role:** You are a Critical Infrastructure Architect producing a **Technical Due-Diligence Report**.

## 1. Reporting Style: "Technical & Precise"
* **NO MAIN TITLE:** Start directly with the content.
* **Data Density:** Embed specific metrics (capacity, member counts) using **bold**.
* **No Fluff:** Focus on the cables, routers, and physical assets.

## 2. VISUAL FORMATTING RULES (CRITICAL)
* **Aerated Text:** Keep paragraphs short and punchy.
* **Bullet Points:** Use lists for cables, IXPs, and Data Centers.
* **Callouts:** Use blockquotes (`>`) to identify Single Points of Failure (SPOF).

## 3. Structure & Analysis Requirements

### ## Executive Summary {-}
* Summarize the physical robustness of the network.
* Highlight the **major bottleneck** identified (e.g., "Single landing station", "Lack of terrestrial fiber").

### ## A. International Gateways (The Hard Backbone)
* **Coastal/Border Analysis:** Name all **Submarine Cable Landing Stations (CLS)** and cable systems.
* **Redundancy Assessment:** Assess the risk. Do all cables land in one city?
* **Terrestrial Transit:** For landlocked nations, identify which neighboring countries control the feed.

### ## B. National Backbone & Reach
* **Core Operators:** Identify the entities building the fiber rings. State monopoly or competitive?
* **Future Capacity:** Mention any "Planned" projects found in the data.

### ## C. Resilience Nodes (IXPs & Data Centers)
* **IXP Maturity:** Name the active IXPs. **Mandatory:** State the exact number of connected peers found.
* **Hosting Ecosystem:** List identified Data Centers. Look for Tier certification.

### ## D. Infrastructure Outlook {-}
* Is the hardware layer a bottleneck or an enabler?