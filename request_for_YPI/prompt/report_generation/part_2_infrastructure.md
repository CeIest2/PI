# Section 2: Physical Infrastructure & Connectivity

**Role:** Chief Infrastructure Architect.

## 1. Target Audience: "The Policy Maker"
* **Who:** Ministry of Infrastructure, Urban Planners, Disaster Relief Agencies.
* **Requirement:** Treat the internet as **Physical Assets** (Buildings, Trenches, Towers). Explain the "Hardware" of the country.
* **Tone:** Tangible, Logistical, Alert-Driven.

## 2. The "Parallel Execution" Scope (Strict Boundaries)
* **SCOPE:** Focus **ONLY** on the physical hardware: Fiber Optic availability, Data Center facilities (concrete buildings), Mobile Towers (4G/5G coverage zones), IXPs (Physical switches), and Spectrum.
* **⛔ CRITICAL NEGATIVE CONSTRAINT (Security):** Do **NOT** discuss **RPKI**, **BGP Hijacking**, or **DDoS**. These are logical protocols, not physical infrastructure. Reserve them for Section 5.
* **⛔ CRITICAL NEGATIVE CONSTRAINT (Market):** Do **NOT** list subscriber market shares (e.g., "34% of users"). Focus on **Network Reach** (e.g., "90% of households covered by fiber").
* **⛔ CRITICAL NEGATIVE CONSTRAINT (Governance):** Do **NOT** discuss laws like NIS2 or GDPR here. Focus on the *result* of investments (e.g., "New towers built"), not the *legislation*.

## 3. Mandatory IRI Data Points (Search & Analyze)
You must search for information related to these specific resilience indicators. Even if the exact index score is unknown, find the underlying data:

* **Data Center Coverage (Physical Hosting):**
    * *Search Query:* "Colocation data centers map [Country Name]" and "Hyperscale data centers locations [Country Name]".
    * *Focus:* Are data centers centralized in one city (risk of disaster) or distributed? Mention key facilities (e.g., "Telehouse", "Equinix").
* **Fiber Ecosystem (The "Last Mile"):**
    * *Search Query:* "FTTH penetration rate [Country Name]" and "National Broadband Plan [Country Name] progress".
    * *Focus:* Is there a **Digital Divide**? Does fiber reach rural villages or just the capital?
* **IXP Coverage (Local Efficiency):**
    * *Search Query:* "List of Internet Exchange Points in [Country Name]" (e.g., France-IX).
    * *Focus:* Does local traffic stay local, or does it detour through a foreign country due to lack of IXPs?
* **Mobile Connectivity & Spectrum:**
    * *Search Query:* "5G population coverage percentage [Country Name]" and "Mobile spectrum auction results [Country Name]".
    * *Focus:* Do we have real 5G capacity (High-band) or just marketing 5G? Are there "White Spots" (No coverage zones)?

## 4. Deep-Dive Analysis Requirements

### ## Executive Summary: The Hardware Health Check {-}
* **The Analogy:** Compare the internet network to a road network. Is it a modern highway system or a crumbling dirt road?
* **Major Alert:** Highlight the single biggest *physical* bottleneck (e.g., "Everything is in Paris", "Rural areas are disconnected").

### ## A. The National Backbone & Fiber Ecosystem
* **Fiber Reach (FTTH):** Analyze the depth of the fiber network. Is the country fully fiber-optic (modern) or still relying on copper/ADSL (obsolete)?
* **The Digital Divide:** Explicitly analyze the gap between major cities and rural areas.

### ## B. Data Centers & Cloud Readiness (The "Warehouses")
* **Physical Locations:** Where are the servers physically stored? (e.g., "Concentrated in Marseille and Paris").
* **Sovereignty Impact:** If there are no local Tier 3/4 data centers, explain that foreign investors will store data in neighboring countries instead.

### ## C. Mobile Connectivity & Spectrum Assets
* **Coverage Quality:** Beyond "bars on the phone", is there real 4G/5G capacity for the population?
* **Spectrum:** Has the government released sufficient spectrum (the "invisible highways") for operators to function?

### ## D. Infrastructure Outlook {-}
* **Capacity Gap:** Can the current *hardware* support the AI/Cloud boom of the next 5 years?