# Automated Recommendation Engine for Enhancing Internet Resilience

## Overview

An agentic system that combines technical infrastructure data from the Internet Yellow Pages (IYP) Neo4j database with real-time web research to generate comprehensive policy recommendations for improving national internet resilience. The engine uses a two-phase AI approach: investigative research followed by strategic synthesis.

## Purpose

The Internet Resilience Index (IRI) measures a country's internet resilience across four pillars, but understanding why scores are low and what to do requires both technical analysis and contextual understanding. This project automates that process by:

1. Querying infrastructure and network topology data from Neo4j
2. Conducting web research for policy context, recent events, and regulations
3. Synthesizing both data streams into actionable strategic reports
4. Providing prioritized recommendations with implementation roadmaps

## Architecture
```
request_for_YPI/
├── generate_report.py        # Main orchestrator (two-phase agentic workflow)
├── src/
│   ├── agents/
│   │   └── graph.py          # LangGraph agent definition with tool routing
│   ├── tools/
│   │   ├── google.py         # Google Custom Search integration
│   │   ├── scraper.py        # Web page and PDF content extraction
│   │   └── neo4j.py          # Database query execution tool
│   └── utils/
│       ├── llm.py            # LLM configuration (fast/smart/reasoning modes)
│       ├── formatting.py     # Neo4j result formatting with Jinja2
│       ├── loaders.py        # File and YAML loaders
│       └── pdf_extractor.py  # PDF text extraction with PyMuPDF
├── prompt/
│   ├── render_document_thinking.txt  # Expert system prompt for reasoning phase
│   └── render_document_based.txt     # Legacy prompt template
├── infrastructure/           # Pillar 1: IXPs, data centers
├── preparation_marche/       # Pillar 2: Peering, competition, domains
├── performance/              # Pillar 3: Speed metrics
└── securite/                 # Pillar 4: MANRS, IPv6, DNSSEC, DDoS
```

Each indicator directory contains:
- `*.cypher` - Progressive queries building complete analysis
- `*.md` - Technical documentation and analysis plans
- `query_templates.yaml` - Jinja2 templates for formatting Neo4j results

## Two-Phase Agentic Architecture

### Phase 1: Investigation (Agentic Research)

Uses LangGraph to orchestrate an autonomous agent that:
- Executes Neo4j queries via the `run_infrastructure_query` tool
- Searches the web for policy documents, news, and regulations via `search_google`
- Reads and extracts content from web pages and PDFs via `read_web_page`
- Decides autonomously which tools to use and when to stop researching

Model: Configurable (fast=Mistral Small, smart=Mistral Large)

### Phase 2: Strategic Synthesis (Reasoning Mode)

Uses a reasoning model to:
- Analyze the complete investigation history
- Correlate quantitative metrics with qualitative context
- Perform root cause analysis linking technical issues to policy gaps
- Generate comprehensive reports following expert prompt structure
- Provide prioritized, actionable recommendations

Model: Magistral (Mistral's reasoning model)

## IRI Coverage

Fully Supported Indicators:
- IXP Coverage, Peering Efficiency, Domain Analysis
- Market Competition (HHI), Transit Dependency
- MANRS Adoption, IPv6 Deployment, DNSSEC Analysis
- DDoS Protection (CDN presence)

Not Supported:
- Performance metrics (requires Ookla data)
- HTTPS adoption (requires certificate data)
- Economic indicators (requires external pricing data)

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Database Setup

 - Use Internet Society's Public Instance:
```python
URI = 'neo4j://iyp-bolt.ihr.live:7687'
AUTH = None
```


### API Keys Configuration

Create a `.env` file:
```bash
MISTRAL_API_KEY=your_key
GOOGLE_API_KEY=your_key
GOOGLE_CX_ID=your_key
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=your_key
LANGCHAIN_ENDPOINT=your_key
LANGCHAIN_TRACING_V2="True"
```
### Obtaining API Keys

**Mistral AI**: Create an account at https://console.mistral.ai and generate an API key from the dashboard. Requires a payment method for production use.

**Google Custom Search**: Visit https://console.cloud.google.com to create a project, enable the Custom Search API, and generate credentials. Then create a Custom Search Engine at https://programmablesearchengine.google.com to obtain your CX ID.

**LangSmith** (Optional): Sign up at https://smith.langchain.com for conversation tracing and debugging. Free tier available for development.


### Usage

Generate a comprehensive report for an indicator:
```bash
python request_for_YPI/generate_report.py infrastructure/ixp_coverage --country=FR --mode=smart
```

Parameters:
- `indicator_input`: Partial or full path to indicator folder
- `--country`: ISO country code (default: FR)
- `--domain`: Domain name for analysis (default: gouv.fr)
- `--asn`: AS number (default: 16276)
- `--mode`: Research phase model - 'fast' or 'smart' (default: smart)

### Testing Queries

Test a single query:
```bash
python testfiles/request_testing.py request_for_YPI/securite/hygiene_routage/score_manrs/1.cypher --country=FR
```

Test query with LLM formatting preview:
```bash
python testfiles/run_query.py request_for_YPI/preparation_marche/localisation_trafic/efficacite_peering/1.cypher --country=FR
```

Run all queries validation suite:
```bash
python testfiles/unit_test_request.py
```

## Report Structure

Generated reports include:

1. Executive Summary - Current state, key findings, resilience assessment
2. Detailed Technical Analysis - Quantitative metrics with qualitative context
3. Risk Assessment Matrix - Technical, operational, and strategic risks
4. Strategic Recommendations Framework
   - Short-term (0-12 months)
   - Medium-term (1-3 years)
   - Long-term (3-5 years)
   - Each with: complexity, cost, impact, stakeholders, KPIs
5. Prioritization Framework - Quick wins vs strategic investments
6. Implementation Roadmap - Quarterly breakdown with dependencies
7. Measurement & Monitoring Framework - KPIs and review schedule
8. Risk Mitigation & Contingency Planning
9. Funding Strategy
10. International Best Practices & Case Studies

## Key Concepts

- **IRI**: Internet Resilience Index - Composite score measuring resilience across Infrastructure, Market Preparation, Performance, and Security pillars
- **IYP**: Internet Yellow Pages - Graph database mapping global internet topology, peering relationships, and routing security
- **Agentic Workflow**: AI agent autonomously decides which data sources to query and when sufficient information has been gathered
- **Two-Phase Architecture**: Separate research phase (breadth) from synthesis phase (depth)
- **Query Pattern**: Overview → Metrics → Gaps → Recommendations

## LLM Modes

The system supports three operational modes:

- **fast**: Mistral Small - Quick processing for web scraping and summarization
- **smart**: Mistral Large - Balanced performance for research and analysis
- **reasoning**: Magistral - Advanced reasoning for strategic synthesis (Phase 2 only)

## Development

Adding new indicators:

1. Create directory under appropriate pillar
2. Write progressive `.cypher` queries (1.cypher, 2.cypher, etc.)
3. Document analysis approach in `.md` file
4. Add formatting templates in `query_templates.yaml`
5. Test with validation suite: `python testfiles/unit_test_request.py`

## Output

Reports are saved in Markdown format in the indicator directory:
```
report_{indicator_name}_countryCode-{CC}_domainName-{domain}_hostingASN-{asn}.md
```

## Dependencies

Core libraries:
- neo4j - Database connectivity
- langchain / langgraph - Agentic framework
- langchain-mistralai - LLM integration
- trafilatura - Web content extraction
- PyMuPDF - PDF text extraction
- Jinja2 / PyYAML - Template rendering
- requests / beautifulsoup4 - HTTP and parsing

## Status

Active Development | Version 0.3 | Last Updated: January 2026