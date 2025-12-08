# Automated Recommendation Engine for Enhancing Internet Resilience

## 📋 Overview

An automated system that analyzes technical internet infrastructure data to generate actionable recommendations for policymakers. The engine queries the Internet Yellow Pages (IYP) Neo4j database and translates complex network data into policy-relevant insights based on the Internet Resilience Index (IRI) framework.

## 🎯 Purpose

The IRI measures a country's internet resilience across four pillars, but understanding *why* scores are low and *what to do* requires deep technical analysis. This project automates that process by:

1. Querying infrastructure and network topology data
2. Analyzing gaps and dependencies
3. Formatting results for LLM-based recommendation generation

## 🏗️ Architecture

```
request_for_YPI/
├── formating.py              # Formats Neo4j results for LLM
├── run_query.py              # Executes queries with formatting
├── unit_test_request.py      # Batch tests all queries
│
├── infrastructure/           # Pillar 1: IXPs, data centers
├── preparation_marche/       # Pillar 2: Peering, competition, domains
├── performance/              # Pillar 3: Speed metrics (external data)
└── securite/                 # Pillar 4: MANRS, IPv6, DNSSEC, DDoS
```

Each indicator contains:
- `*.cypher` - Progressive queries building a complete analysis
- `*.md` - Technical documentation and analysis plan
- `query_templates.yaml` - Jinja2 templates for LLM formatting

## 📊 IRI Coverage

**Fully Supported (✅):**
- IXP Coverage, Peering Efficiency, Domain Analysis
- Market Competition (HHI), Transit Dependency
- MANRS Adoption, IPv6 Deployment, DNSSEC Analysis
- DDoS Protection (CDN presence)

**Not Supported (❌):**
- Performance metrics (Ookla data required)
- HTTPS adoption (certificate data needed)
- Economic indicators (pricing data external)

## 🚀 Quick Start

### Setup
```bash
pip  install -r requirements.txt
```

If you want you can install IYP on your machine following this page: : https://github.com/InternetHealthReport/internet-yellow-pages

And run 
```bash
docker start iyp
```

Configure Neo4j connection in Python files:

For local testing:
```python
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")
```

For using the server of interet society 
```python
URI = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH = None

```

Setup your Mistral API key
```bash
export MISTRAL_API_KEY="your_key_"
```

Setup your SERPAPI_API_KEY
```bash
export SERPAPI_API_KEY="your_key_"
```

### Usage


**Generate markdown document with LLM for an given index**
```bash
python render_document.py index_name --country='country_indicator' --domain='domain.gouv' --asn='AS_number'
```

**Test a single query:**
```bash
python request_for_YPI/request_testing.py request_for_YPI/securite/hygiene_routage/score_manrs/1.cypher --country='FR'
```

**Test a specific query and visualize the text format for LLM:**
```bash
python request_for_YPI/run_query.py request_for_YPI/preparation_marche/localisation_trafic/efficacite_peering/1.cypher --country='FR'
```

**Run all queries:**
```bash
python request_for_YPI/unit_test_request.py
```

## 🔍 Example: IXP Coverage Analysis

For a country with poor IXP coverage:

1. **Query 1**: List IXPs and their locations
2. **Query 2**: Count local vs international members
3. **Query 3**: Identify major networks not peering locally

Result: Actionable list of networks to target for IXP membership campaigns.

## 🎓 Key Concepts

- **IRI**: Composite score measuring internet resilience (Infrastructure, Market, Performance, Security)
- **YPI**: Graph database mapping internet topology, peering relationships, and routing security
- **Query Pattern**: Overview → Metrics → Gaps → Recommendations

## 🛠️ Development

Adding new indicators:
1. Create directory with `*.cypher` queries
2. Write analysis plan in `*.md`
3. Add YAML formatting templates
4. Test with `unit_test_request.py`


---

**Status**: Active Development | **Version**: 0.2 | **Last Updated**: November 2025