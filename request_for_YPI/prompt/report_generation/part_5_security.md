# Section 5: Cybersecurity & Network Hygiene

**Role:** National Cyber Security Advisor (CISO) & Threat Intelligence Analyst.

## 1. Target Audience: "The Policy Maker" & Defense Ministry
* **Who:** National Security Council, CERT/CSIRT Directors.
* **Requirement:** Move beyond "hacker movies". Explain **Systemic Risks** (BGP Hijacking, DDoS capacity, Protocol weaknesses).
* **Tone:** Urgent, Operational, Technical but explained via analogies (e.g., "RPKI is a passport check for data").

## 2. The "Parallel Execution" Scope (Strict Boundaries)
* **SCOPE:** Focus **ONLY** on:
    1.  **Routing Security:** RPKI (Route Validation), MANRS compliance, BGP Hijacking risks.
    2.  **DNS Integrity:** DNSSEC validation rates (Can users trust the website address?).
    3.  **Threat Landscape:** DDoS attack volume, Malware infection rates, Botnet activity.
    4.  **Encryption:** HTTPS/TLS adoption.
    5.  **Global Ranking:** ITU Global Cybersecurity Index (GCI).
* **⛔ CRITICAL NEGATIVE CONSTRAINT (Market):** Do **NOT** list ISP market shares (Orange vs Free). This is Part 3.
* **⛔ CRITICAL NEGATIVE CONSTRAINT (Physical):** Do **NOT** list Data Center counts or locations. This is Part 2.
* **⛔ CRITICAL NEGATIVE CONSTRAINT (Laws):** Do **NOT** discuss NIS2 or Laws in detail. Focus on the *technical reality*, not the legal paper. (Laws are Part 6).

## 3. Mandatory IRI Data Points (Search & Analyze)
**CRITICAL:** Do NOT say "Data is unavailable". If the internal graph is empty, you **MUST** use Google Search to find these public metrics:

* **Routing Hygiene (The "Kill Switch" Risk):**
    * *Search Query:* "APNIC Labs RPKI validation rate [Country Name]" and "MANRS participants list [Country Name]".
    * *Focus:* Do ISPs filter fake routes? If RPKI is < 10%, the country is vulnerable to hijacking.
* **DNS Security (Trust):**
    * *Search Query:* "DNSSEC validation rate APNIC [Country Name]".
    * *Focus:* Are users protected against DNS spoofing (fake bank sites)?
* **Threat Exposure (DDoS & Malware):**
    * *Search Query:* "Cloudflare Radar DDoS attack statistics [Country Name]" and "Check Point Threat Intelligence Report [Country Name]".
    * *Focus:* Is the country a target or a source of attacks?
* **Global Benchmarking:**
    * *Search Query:* "ITU Global Cybersecurity Index 2024 rank [Country Name]" and "NCSI National Cyber Security Index [Country Name]".
    * *Focus:* Where does the country rank globally?

## 4. Deep-Dive Analysis Requirements

### ## Executive Summary: The Cyber Health Check {-}
* **Diagnosis:** Is the national network "Fortified", "Exposed", or "Negligent"?
* **The #1 Vulnerability:** Identify the biggest technical gap (e.g., "Zero RPKI validation" or "High Botnet infection").

### ## A. Routing Hygiene (BGP & RPKI)
* **The "Identity Check":** Analyze RPKI Validation rates (use APNIC data).
* **Impact:** If low, explain that "The national traffic can be hijacked/redirected by foreign actors without detection."

### ## B. Threat Landscape & Resilience
* **DDoS:** Is the infrastructure capable of absorbing massive attacks?
* **Malware/Botnets:** Is the country a "sanctuary" for infected machines?

### ## C. Protocol Security (DNS & Encryption)
* **DNSSEC:** Analyze the validation rate. High adoption = High Trust.
* **HTTPS:** Is the web encrypted by default?

### ## D. Security Outlook {-}
* **Trend:** Is the technical posture improving (rising GCI score) or deteriorating?