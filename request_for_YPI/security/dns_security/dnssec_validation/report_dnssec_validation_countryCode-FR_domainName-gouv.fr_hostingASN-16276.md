# Internet Resilience Policy Report

## Executive Summary

The country's Internet resilience posture is critically vulnerable due to complete lack of adoption of routing security best practices. With 2233 total Autonomous System Numbers (ASNs) and 0% participation in MANRS (Mutually Agreed Norms for Routing Security), the national routing infrastructure is exposed to common routing threats. Compounding this vulnerability, two major ISPs (Orange S.A. serving 34.5% and SFR Group serving 17.9% of the population) dominate the market without MANRS participation, creating significant single points of failure. This concentration means that routing security incidents affecting either provider could impact over half the population.

Priority recommendations include immediate engagement with major ISPs to adopt MANRS, development of national routing security policies, and establishment of incentives for broader MANRS adoption across all AS operators. Given the complete absence of routing security measures, the overall resilience grade is assessed as **Critical** requiring urgent intervention.

## Detailed Technical Analysis

### Current State Assessment

- **Total ASNs**: 2233
- **MANRS Adoption**: 0 ASNs (0% adoption rate)
- **Population Coverage by Major ASNs**:
  - AS3215 (Orange S.A.): 34.5% of population
  - AS15557 (SFR Group): 17.9% of population
  - Combined: 52.4% of population served by non-MANRS members

### Comparative Analysis

While specific regional benchmarks aren't available in this dataset, a 0% MANRS adoption rate is significantly below global averages where many countries have at least 5-10% of their ASNs participating in MANRS. The market concentration (52.4% of population served by two providers) is higher than typical in developed markets, increasing systemic risk.

### Vulnerability Deep-Dive

**Technical Vulnerabilities:**
- Complete absence of routing security best practices (MANRS)
- High concentration of traffic through two major ASNs without routing security measures
- Potential for route hijacking, leaks, and other common routing attacks

**Operational Vulnerabilities:**
- Lack of diversity in routing security practices
- No evident national policy or regulatory framework for routing security
- Concentration risk with two providers serving majority of population

**Strategic Vulnerabilities:**
- No evident national strategy for routing security
- Lack of incentives for MANRS adoption
- Potential regulatory gaps in addressing routing security

### Strengths and Assets

- Existing technical infrastructure with 2233 ASNs
- Presence of multiple operators (though dominated by two majors)
- Opportunity to establish national leadership in routing security

## Risk Assessment Matrix

| Risk Category | Description | Likelihood | Impact | Risk Level | Mitigation Priority |
|---------------|-------------|------------|--------|------------|---------------------|
| Routing Security | No MANRS adoption across all ASNs | HIGH | HIGH | CRITICAL | 1 |
| Market Concentration | Two providers serve 52.4% of population without MANRS | HIGH | HIGH | CRITICAL | 2 |
| Regulatory Gap | No national policy for routing security | MEDIUM | HIGH | HIGH | 3 |
| Awareness Gap | Likely low awareness of MANRS benefits | HIGH | MEDIUM | MEDIUM | 4 |

## Strategic Recommendations Framework

### Short-Term Actions (0-12 months)

| # | Action | Description | Complexity | Cost | Impact | Stakeholders | KPIs | Dependencies |
|---|--------|-------------|------------|------|--------|--------------|------|--------------|
| 1 | National MANRS Awareness Campaign | Educate ISPs and policymakers about MANRS benefits | LOW | LOW | MEDIUM | Government, ISPs | # of awareness sessions, # of participants | None |
| 2 | Engage Major ISPs | Direct engagement with Orange and SFR to adopt MANRS | MEDIUM | LOW | HIGH | Major ISPs, Regulator | MANRS adoption by major ISPs | Awareness campaign |
| 3 | Establish National Routing Security Task Force | Multi-stakeholder group to develop policy recommendations | MEDIUM | MEDIUM | MEDIUM | Government, ISPs, Academia | Task force established, initial report | None |

**Implementation Details:**
1. **National MANRS Awareness Campaign**:
   - Organize webinars and workshops targeting network operators
   - Develop localized educational materials about MANRS
   - Timeline: Months 1-3
   - Success criteria: 50% of major ISPs participate in awareness sessions

2. **Engage Major ISPs**:
   - Direct meetings with Orange and SFR leadership
   - Present business case for MANRS adoption
   - Offer technical assistance for implementation
   - Timeline: Months 2-6
   - Success criteria: At least one major ISP commits to MANRS adoption

3. **Establish National Routing Security Task Force**:
   - Recruit stakeholders from government, ISPs, and academia
   - Hold initial meeting to define scope and goals
   - Timeline: Months 1-4
   - Success criteria: Task force established with clear mandate

### Medium-Term Actions (1-3 years)

| # | Action | Description | Complexity | Cost | Impact | Stakeholders | KPIs | Dependencies |
|---|--------|-------------|------------|------|--------|--------------|------|--------------|
| 1 | Develop National Routing Security Policy | Create regulatory framework encouraging MANRS adoption | HIGH | MEDIUM | HIGH | Government, Regulator | Policy document approved | Task force recommendations |
| 2 | MANRS Incentive Program | Create incentives for ISPs to adopt MANRS | MEDIUM | MEDIUM | HIGH | Government, ISPs | # of ISPs adopting MANRS | National policy |
| 3 | Establish Local IXP Security Standards | Develop security requirements for IXPs | MEDIUM | LOW | MEDIUM | IXPs, Government | # of IXPs meeting standards | None |

**Implementation Details:**
1. **Develop National Routing Security Policy**:
   - Task force develops policy recommendations
   - Government consults with industry
   - Policy draft completed and approved
   - Timeline: Months 6-18
   - Success criteria: Policy approved and published

2. **MANRS Incentive Program**:
   - Design incentive program (tax breaks, grants, recognition)
   - Launch program and promote to ISPs
   - Timeline: Months 12-24
   - Success criteria: 20% of ISPs participate in incentive program

### Long-Term Actions (3-5 years)

| # | Action | Description | Complexity | Cost | Impact | Stakeholders | KPIs | Dependencies |
|---|--------|-------------|------------|------|--------|--------------|------|--------------|
| 1 | Mandatory MANRS for Large ISPs | Require MANRS adoption for ISPs serving >10% of population | HIGH | LOW | HIGH | Government, Large ISPs | % of large ISPs complying | National policy |
| 2 | National Routing Security Monitoring | Establish monitoring system for routing incidents | HIGH | HIGH | HIGH | Government, Technical community | Monitoring system operational | None |
| 3 | Regional MANRS Leadership | Position country as regional leader in routing security | MEDIUM | MEDIUM | MEDIUM | Government, Industry | # of regional initiatives led | National policy |

**Implementation Details:**
1. **Mandatory MANRS for Large ISPs**:
   - Develop regulatory requirements
   - Phase in requirements for largest ISPs first
   - Timeline: Years 3-4
   - Success criteria: All ISPs serving >10% of population comply with MANRS

## Prioritization Framework

**Priority Matrix:**
```
High Impact, Low Effort    │ High Impact, High Effort
[Quick Wins - DO FIRST]   │ [Strategic Projects]
Engage Major ISPs         │ Develop National Policy
Awareness Campaign        │ MANRS Incentive Program
                           │
─────────────────────────────────────────────
                           │
Low Impact, Low Effort     │ Low Impact, High Effort
[Fill-ins]                │ [Avoid]
Establish Task Force      │
```

**Recommended Execution Sequence:**
1. Launch National MANRS Awareness Campaign → Engage Major ISPs → Establish Task Force
   - Rationale: Build awareness and engagement before developing policy
2. Develop National Policy → MANRS Incentive Program → Mandatory Requirements
   - Rationale: Create policy foundation before implementing incentives and requirements

## Implementation Roadmap

**Year 1:**
- Q1: Launch awareness campaign, initial stakeholder engagement
- Q2: Engage major ISPs, establish task force
- Q3: Task force develops initial recommendations
- Q4: Begin policy development process

**Years 2-3:**
- Finalize and implement national routing security policy
- Launch MANRS incentive program
- Begin establishing IXP security standards

**Years 4-5:**
- Implement mandatory MANRS requirements for large ISPs
- Establish national routing security monitoring system
- Position country as regional leader in routing security

## Measurement & Monitoring Framework

**Key Performance Indicators:**

| Timeframe | Metric | Baseline | Target | Measurement Method | Review Frequency |
|-----------|--------|----------|--------|-------------------|------------------|
| 6 months | % of major ISPs engaged on MANRS | 0% | 100% | Stakeholder meetings | Quarterly |
| 1 year | MANRS adoption by major ISPs | 0 | 1 | MANRS membership data | Quarterly |
| 3 years | % of ASNs with MANRS adoption | 0% | 20% | MANRS membership data | Annual |
| 5 years | % of population served by MANRS members | 0% | 80% | MANRS membership + population data | Annual |

**Monitoring Mechanisms:**
- Regular data collection from MANRS membership records
- Quarterly reports from ISPs on routing security practices
- Annual national Internet resilience assessment

## Risk Mitigation & Contingency Planning

For high-priority actions:
1. **Major ISP Engagement Risk**: If major ISPs resist MANRS adoption
   - Early warning: Lack of engagement in initial meetings
   - Contingency: Develop regulatory incentives or requirements
   - Exit strategy: Focus on medium-sized ISPs first

2. **Policy Development Risk**: Delays in government approval
   - Early warning: Slow progress in policy drafting
   - Contingency: Implement voluntary measures first
   - Exit strategy: Focus on industry-led initiatives

## Funding Strategy

- **Estimated total investment required**: $500,000 - $1,000,000 over 5 years
- **Potential funding sources**:
  - National cybersecurity budget
  - International donors (ITU, World Bank)
  - Industry contributions
  - Public-private partnerships
- **Phased funding approach**:
  - Year 1: $100,000 (awareness, engagement)
  - Years 2-3: $300,000 (policy development, incentives)
  - Years 4-5: $500,000 (monitoring, mandatory requirements)

## International Best Practices & Case Studies

1. **United States**: Established MANRS initiative with government support
   - Lesson: Government endorsement accelerates adoption
   - Adaptation: Develop local MANRS chapter with government backing

2. **Brazil**: Incorporated routing security in national cybersecurity strategy
   - Lesson: Policy integration ensures sustained focus
   - Adaptation: Include MANRS requirements in national broadband plan

3. **Netherlands**: Mandatory routing security for critical infrastructure
   - Lesson: Regulatory requirements drive compliance
   - Adaptation: Phase in requirements starting with largest providers

This report provides a comprehensive roadmap for improving national Internet resilience through routing security improvements. Immediate action to engage major ISPs and develop national policy is recommended to address the critical vulnerabilities identified.