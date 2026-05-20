import requests
import json
import os
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"

def call_ollama(
    prompt: str,
    model: str = "deepseek-r1",
    temperature: float = 0.1,
    timeout: int = 120
) -> str:
    """Call Ollama with fallback to intelligent demo mode."""

    # Check if demo mode
    if os.environ.get("GIDBOY_DEMO", "0") == "1":
        return generate_contextual_response(prompt)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.3,
            "num_ctx": 8192,
        }
    }

    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        res.raise_for_status()
        return res.json()["response"]

    except requests.exceptions.ConnectionError:
        return "ERROR: Ollama not running. Start with: ollama serve"
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out. Try a shorter query or smaller model."
    except requests.exceptions.HTTPError as e:
        if "404" in str(e):
            return f"ERROR: Model '{model}' not found. Run: ollama pull {model}"
        return f"ERROR: HTTP {e}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def generate_contextual_response(prompt: str) -> str:
    """Generate contextual response based on query content."""
    import re

    # Extract mode from prompt
    mode_match = re.search(r"MODE:\s*(\w+)", prompt)
    mode = mode_match.group(1).upper() if mode_match else "RESEARCH"

    # Extract the actual query/task
    task_match = re.search(r"TASK:\s*(.+?)(?=\n\nINSTRUCTIONS:)", prompt, re.DOTALL)
    task = task_match.group(1).strip() if task_match else ""

    task_lower = task.lower()

    # Route to appropriate response generator
    if "liquidity" in task_lower or "lp" in task_lower:
        if "solana" in task_lower:
            return generate_solana_lp_research()
        return generate_liquidity_research()
    elif "firedancer" in task_lower or "validator" in task_lower:
        return generate_firedancer_research()
    elif "defi" in task_lower or "protocol" in task_lower:
        return generate_defi_analysis()
    elif "ai" in task_lower or "agent" in task_lower:
        return generate_ai_signal()
    elif "grant" in task_lower or "job" in task_lower or "fellowship" in task_lower:
        return generate_opportunities()
    elif "analyze" in task_lower or "data" in task_lower:
        return generate_analysis()
    elif "signal" in task_lower or "trend" in task_lower:
        return generate_signal()
    elif "content" in task_lower or "thread" in task_lower:
        return generate_content()
    elif "career" in task_lower:
        return generate_career()
    elif "execute" in task_lower or "apply" in task_lower:
        return generate_execution()
    else:
        return generate_default_research(task)

def generate_solana_lp_research() -> str:
    """Deep research on Solana Liquidity Provision."""
    return """## EXECUTIVE SUMMARY
Solana's liquidity provision ecosystem differs fundamentally from Ethereum L1s through its high-frequency, low-latency architecture enabling novel market-making strategies. However, unique challenges around MEV extraction, impermanent loss dynamics, and concentrated liquidity management require specialized solutions.

## PROBLEM IDENTIFICATION
**Current State:**
- Concentrated liquidity (CL) dominates with 85%+ of DEX volume on Solana
- Jupiter captures 70% of aggregator volume, creating centralization risk
- MEV extraction via Jito bundles reaches $50M+ monthly
- Impermanent loss (IL) averages 15-25% annually for wide-range LPs
- LP churn rate of 60% within first 90 days

**Solana-Specific Problems:**

1. **Speed-Induced Volatility**
   - 400ms finality creates micro-arbitrage opportunities
   - High-frequency rebalancing drains LP value
   - Flash loan attacks execute in single slot

2. **MEV Sandwiching**
   - Jito bundles enable atomic arbitrage
   - 40% of trades subject to sandwich attacks
   - LPs lose 2-5% annually to MEV extraction

3. **Concentrated Liquidity Complexity**
   - Active management requires constant rebalancing
   - 70% of positions go out-of-range within 30 days
   - Gas costs (though low) accumulate with frequency

4. **Oracle Latency**
   - Pyth updates every 400ms vs Ethereum's ~12s
   - Price deviation creates arbitrage against LPs
   - Stale oracle risks during network congestion

## DATA & EVIDENCE
**Solana LP Metrics vs Ethereum:**
| Metric | Solana | Ethereum | Advantage |
|--------|--------|----------|-----------|
| Avg Trade Size | $450 | $2,800 | Higher volume |
| Trade Frequency | 28M/day | 1.2M/day | 23x more |
| LP APR Range | 15-120% | 5-45% | Higher yields |
| IL Incidence | 68% | 52% | More risk |
| Rebalancing Cost | $0.002 | $15 | 7500x cheaper |
| Time to IL | 14 days | 45 days | Faster loss |

**Orca Whirlpool Data (90-day):**
```
TVL Distribution:
Whirlpools: $450M TVL
├─ SOL/USDC: $120M (26%)
├─ USDC/USDT: $85M (19%)
├─ BONK/SOL: $65M (14%)
└─ Others: $180M (41%)

Fee Revenue:
Daily: $180K average
├─ SOL pairs: 65% of fees
├─ Stable pairs: 20%
└─ Altcoin: 15%

LP Retention:
Week 1: 100%
Week 4: 42%
Week 12: 18%
```

## WORKFLOW ANALYSIS
**Traditional LP Workflow:**
```
Deposit → Monitor Range → Rebalance → Withdraw
   ↓           ↓              ↓          ↓
[Capital]  [Check q/d]   [Gas costs]  [IL Realized]
          [4x daily]    [Compounding]  [Exit Loss]
```

**Solana LP Workflow (Problems):**
```
Deposit → HFT Arb → MEV Extract → Rebalance → Repeat
   ↓          ↓          ↓           ↓         ↓
[Enter]   [Front-run] [Sandwich] [Gas]   [Value Leak]
```

**Bottlenecks Identified:**
1. Manual rebalancing can't match 400ms finality
2. Range selection requires predictive modeling
3. MEV protection adds 20-30% gas overhead
4. Cross-DEX arbitrage drains pool depth

## SOLANA-SPECIFIC DIFFERENTIATORS
**1. Concentrated Liquidity as Default**
- Unlike Ethereum's 50/50 AMM history, Solana skipped to CL
- Whirlpools, Raydium CLMM dominate
- Requires active management vs passive holding

**2. Jito-MEV Integration**
- Blockspace auction creates "fair" MEV extraction
- LPs can participate in tip revenue
- Bundle atomicity prevents failed rebalances

**3. Programmability at Speed**
- JIT (Just-In-Time) liquidity possible
- Flash loans enable complex arbitrage
- Automated strategies execute in single transaction

**4. Composability Architecture**
- Single-liquidity-multiple-protocols (Sanctum)
- Jupiter routing across 20+ DEXs
- LP tokens as collateral (Solend, MarginFi)

## VISUAL FRAMEWORK
**LP Value Flow:**
```
Trader Order
      ↓
Jupiter Aggregator
      ↓
┌─────────────┐
│  Route      │ → AMM 1 (60%) → Fee 0.3%
│  Selection  │ → AMM 2 (30%) → Fee 0.5%
└─────────────┘ → AMM 3 (10%) → Fee 1.0%
      ↓
MEV Bot (Sandwich)
      ↓
LP receives: Fee - MEV - IL
```

**Impermanent Loss Curve:**
```
IL %
50% │                    ╭─────
    │                 ╭──╯
30% │              ╭──╯
    │           ╭──╯
15% │        ╭──╯
    │     ╭──╯
 5% │  ╭──╯
    │ ╱
 0% └──────────────────→
    -50%  -25%  0   +25%  +50%
              Price Deviation
```

## SOLUTIONS PROPOSED
**Solution 1: Automated JIT Liquidity**
- Problem: Capital inefficient to maintain full-range liquidity
- Approach: Flash mint LP positions only when trade arrives
- Implementation: JIT program integrated with router
- Resources: Rust development, Jito bundle integration
- Timeline: 6 months
- Expected Impact: 40% capital efficiency gain
- Risks: Smart contract complexity, audit requirements

**Solution 2: MEV-Protected LP Vaults**
- Problem: Retail LPs losing to MEV extraction
- Approach: Aggregate LP positions with MEV redistribution
- Implementation: Vault contract + Jito tip sharing
- Resources: $50K development, $200K audits
- Timeline: 3 months
- Expected Impact: Return 60% of MEV to LPs
- Risks: Regulatory scrutiny on MEV

**Solution 3: AI-Driven Range Optimization**
- Problem: 70% of positions go out-of-range
- Approach: ML model predicts optimal tick range
- Implementation: Off-chain model + on-chain execution
- Resources: Data science team, historical DEX data
- Timeline: 4 months
- Expected Impact: Reduce IL by 35%
- Risks: Model accuracy, latency of predictions

**Solution 4: Cross-Protocol Liquidity Aggregation**
- Problem: Fragmented liquidity across DEXs
- Approach: Unified LP position across Orca/Raydium/Phoenix
- Implementation: Liquidity router with position rebalancing
- Resources: Protocol integrations, SDK development
- Timeline: 8 months
- Expected Impact: 25% better execution for traders
- Risks: Protocol upgrade dependencies

## ACTIONABLE ROADMAP
**Immediate (0-7 days):**
- Analyze current LP positions for IL exposure
- Research JIT liquidity implementations (Cycloi, Kamino)
- Join Solana LP Discord communities for alpha

**Short-term (1-4 weeks):**
- Deploy test LP position with narrow range
- Benchmark IL vs fees earned
- Experiment with Jito bundle submission

**Medium-term (1-3 months):**
- Evaluate automated vault strategies (Kamino, Francium)
- Build custom rebalancing bot
- Document Solana-specific LP playbook

## MONITORING METRICS
**Key Indicators:**
- Personal IL rate vs market average
- Fee APR vs impermanent loss
- Time in-range percentage
- MEV extracted from positions

**Success Criteria:**
- IL < 10% annually
- Fee income > IL by 2x
- 80%+ time in-range
- Rebalancing cost < 5% of yield

END."""

def generate_liquidity_research() -> str:
    """General blockchain liquidity provision research."""
    return """## EXECUTIVE SUMMARY
Liquidity provision in DeFi represents a $50B+ market securing decentralized exchange operations, yet faces systemic challenges including impermanent loss, MEV extraction, and concentration risks that threaten LP profitability and protocol sustainability.

## PROBLEM IDENTIFICATION
**Current State:**
- $50B+ TVL locked in DEX liquidity pools
- Average LP retention: 45 days
- Impermanent loss affects 60%+ of positions
- MEV extraction: $1B+ annually from LPs
- Concentrated liquidity complexity drives retail exit

**Core Problems:**

1. **Impermanent Loss (IL)**
   - Defined: Loss vs holding assets due to price divergence
   - Impact: $5B+ lost annually across DEXs
   - Average IL: 15-30% annually for volatile pairs

2. **MEV Extraction**
   - Sandwich attacks: 2-5% of trade value
   - JIT liquidity: Front-running LP positions
   - Toxic flow: Informed traders exploiting LPs

3. **Capital Efficiency**
   - Most LPs deploy full-range (inefficient)
   - Concentrated liquidity requires active management
   - Idle capital during out-of-range periods

4. **Asymmetric Information**
   - Informed flow from arbitrageurs
   - Oracle latency exploitation
   - Cross-DEX arbitrage draining pools

## DATA & EVIDENCE
**Global DEX Metrics:**
| Chain | TVL | Daily Volume | Avg Fee | LP APR |
|-------|-----|--------------|---------|--------|
| Ethereum | $15B | $2B | 0.3% | 12-25% |
| Solana | $3B | $1.5B | 0.25% | 25-80% |
| Arbitrum | $2.5B | $800M | 0.3% | 15-30% |
| Base | $800M | $400M | 0.3% | 20-45% |

**Impermanent Loss Study (2024):**
```
Pair Type        IL Rate    Fee Offset    Net Return
ETH/USDC         18%        +22%         +4%
BTC/USDC         12%        +15%         +3%
Memecoin pairs   85%        +45%        -40%
Stable pairs      2%         +6%         +4%
```

## ROOT CAUSE ANALYSIS
**Problem Tree:**
```
                    LP Unprofitability
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
   Impermanent        MEV              Capital
   Loss (40%)         Extraction       Inefficiency
        │             (30%)             (30%)
        │              │                  │
   Price Divergence  Sandwich          Full Range
   Volatility        JIT Bots          Deployment
```

## SOLUTIONS PROPOSED
**Solution 1: Dynamic Fee Adjustment**
- Protocol adjusts fees based on volatility
- High volatility = higher fees to offset IL
- Implementation: Oracle-based fee controller
- Expected: 20-30% IL reduction

**Solution 2: MEV Redistribution**
- Protocol captures MEV, returns to LPs
- Examples: CowSwap, Flashbots Protect
- Expected: 50-70% MEV returned to LPs

**Solution 3: Insurance Protocols**
- Third-party IL insurance
- LPs pay premium for guaranteed returns
- Examples: Nexus Mutual, InsurAce
- Cost: 5-10% of yield for protection

## ACTIONABLE ROADMAP
**Immediate:**
- Calculate personal IL exposure
- Research IL protection protocols
- Evaluate active vs passive LP strategies

**Short-term:**
- Test concentrated liquidity positions
- Explore MEV-protected DEXs
- Diversify across stable and volatile pairs

**Medium-term:**
- Implement automated rebalancing
- Build LP analytics dashboard
- Consider protocol governance participation

END."""

def generate_firedancer_research() -> str:
    """Original Firedancer research response."""
    return """## EXECUTIVE SUMMARY
Solana's validator ecosystem is undergoing a critical transformation with Firedancer's mainnet beta launch in Q1 2025. This represents the first production-grade alternative validator client, addressing network reliability concerns through a C++ implementation delivering 10x throughput improvements.

## PROBLEM IDENTIFICATION
**Current State:**
- Single client dependency creates systemic risk (Agave represents 95%+ of validators)
- Network outages have occurred due to client bugs (notably March 2023, February 2024)
- Throughput bottlenecks at ~50,000 TPS with current architecture
- Validator hardware requirements limit decentralization

**Root Cause Analysis:**
- Surface: Software bugs in Rust implementation causing consensus failures
- Deep: Monoculture risk with single client codebase
- Systemic: Economic incentives favor incumbent client despite risks

## DATA & EVIDENCE
**Key Metrics:**
| Metric | Value | Trend | Source |
|--------|-------|-------|--------|
| Current TPS | 4,000 avg | Stable | Solana Beach |
| Peak TPS | 65,000 | ↓ | SolanaFM |
| Validator Count | 1,800 | ↑ | Solana Docs |
| Client Diversity | 1% non-Agave | ↑ | Validator Dashboard |
| Network Uptime | 99.8% | → | Solana Status |

## WORKFLOW ANALYSIS
**Current Process Flow:**
```
Transaction → Agave Client → Banking Stage → PoH → Consensus → Broadcast
                ↓              ↓            ↓         ↓           ↓
           [Bottleneck]    [Bottleneck] [Latency] [Delay]   [Propagation]
```

## SOLUTIONS PROPOSED
**Solution 1: Graduated Mainnet Rollout**
- Problem addressed: Risk of mass migration causing instability
- Approach: Canary validators → 5% → 25% → 50% thresholds
- Timeline: 12 months
- Success metrics: Uptime >99.9%, client diversity >30%

**Solution 2: Client-Agnostic Infrastructure**
- Problem addressed: Tooling fragmentation
- Approach: Standardized APIs across clients
- Timeline: 6 months
- Success metrics: 10+ tools supporting both clients

END."""

def generate_defi_analysis() -> str:
    """DeFi protocol analysis."""
    return """## ANALYTICAL FRAMEWORK
**Methodology:** Quantitative on-chain analysis
**Data Sources:** DefiLlama, Dune Analytics, Token Terminal
**Time Period:** 90-day rolling
**Confidence Level:** High (85%)

## DATA LANDSCAPE
**Protocol Metrics:**
| Metric | Current | 30d Avg | 90d Avg | Change |
|--------|---------|---------|---------|--------|
| TVL | $2.8B | $2.6B | $2.4B | +16% |
| Daily Revenue | $450K | $420K | $380K | +18% |
| Active Users | 45K | 42K | 38K | +18% |
| Token Price | $2.85 | $2.60 | $2.40 | +18% |

## CORRELATION ANALYSIS
**Key Findings:**
- TVL ↔ Revenue correlation: 0.92 (strong)
- Users ↔ Price correlation: 0.76 (moderate)
- Token unlock events show -15% price impact on average

## TREND ANALYSIS
**Forecast (90-day):**
- Conservative: TVL $3.0B
- Baseline: TVL $3.4B
- Optimistic: TVL $4.0B

END."""

def generate_ai_signal() -> str:
    """AI/crypto signal detection."""
    return """## SIGNAL OVERVIEW
**Signal Strength:** 8/10 | **Urgency:** 7/10 | **Confidence:** 82%
**Category:** Narrative/Technological

## EARLY SIGNALS DETECTED
1. **AI Agent Token Explosion** — Strength: High
   - Indicator: Market cap grew from $100M to $2.4B in 90 days
   - Velocity: +400% QoQ

2. **Autonomous Wallet Activity** — Strength: High
   - Indicator: 50K+ AI-driven TXs/day
   - Precedent: 10x scale difference from 2017 bots

## WHY IT MATTERS
**First-Order:** New asset class - AI agents as economic entities
**Second-Order:** Regulatory attention, talent migration
**Third-Order:** Economic restructuring of labor markets

## EARLY OPPORTUNITIES
**Tactical:** AI infrastructure tokens (Bittensor, Fetch.ai)
**Strategic:** Build specialized trading agents
**Transformational:** AI agent marketplace platform

END."""

def generate_opportunities() -> str:
    """Research opportunities."""
    return """## TOP OPPORTUNITIES

### 1. Messari - Crypto Research Analyst
**What:** Produce sector-specific research reports
**Who For:** Researchers (in crypto)
**Requirements:** Deep DeFi understanding, financial modeling
**Skill Match:** High | **Difficulty:** 7/10
**Action:** Submit writing sample via messari.io/careers

### 2. Open Society Foundations - Digital Rights Grant
**What:** $100K grant for surveillance tech research
**Who For:** Researchers (outside crypto)
**Requirements:** PhD or equivalent, policy engagement
**Skill Match:** Medium | **Difficulty:** 4/10
**Action:** Apply at opensociety.org/grants

### 3. a16z crypto - Research Fellow
**What:** 6-month fellowship in ZK proofs
**Who For:** Advanced researchers
**Requirements:** Cryptographic background, publications
**Skill Match:** High | **Difficulty:** 9/10
**Action:** Email research@a16zcrypto.com

END."""

def generate_analysis() -> str:
    """Generic analysis response."""
    return """## ANALYTICAL FRAMEWORK
**Methodology:** Mixed quantitative/qualitative
**Confidence Level:** High (85%)

## DATA LANDSCAPE
**Raw Data Points:**
| Metric | Current | 7d Avg | 30d Avg | 90d Avg |
|--------|---------|--------|---------|---------|
| Daily Volume | $1.2B | $1.1B | $980M | $850M |
| Active Users | 45K | 42K | 38K | 35K |
| Success Rate | 85% | 83% | 82% | 78% |

## PATTERN IDENTIFICATION
**Emerging Patterns:**
1. Institutional inflow correlation with price stability (0.68)
2. DePIN activity surge: +400% QoQ

**Anomalies:**
- Day 32: Volume spike +340% (airdrop)
- Day 67: Failed TX rate spike to 25%

## INSIGHTS
**Key Findings:**
1. Network activity quality exceeds quantity
2. Institutional adoption driving sustainable growth
3. Throughput headroom sufficient for 10x

## RECOMMENDATIONS
**Priority Actions:**
| Priority | Action | Impact | Timeline |
|----------|--------|--------|----------|
| P0 | Optimize infrastructure | High | 2 weeks |
| P1 | Improve onboarding | High | 1 week |
| P2 | Spam detection | Medium | 1 month |

END."""

def generate_signal() -> str:
    """Generic signal response."""
    return """## SIGNALS
1. AI agent tokens up 400% QoQ with real usage
2. PayPal USD stablecoin volume shifting to Solana
3. Institutional validators increasing stake

## WHY IT MATTERS
- Real transaction volume, not speculation
- Payment rails choosing Solana

## EARLY OPPORTUNITIES
1. AI x DeFi infrastructure
2. Payment SDK integrations
3. Institutional validator tooling

END."""

def generate_content() -> str:
    """Content creation response."""
    return """## X THREAD:
1. Hook: Solana just did something Ethereum couldn't
2. Context: Firedancer validator client launch
3. Key Insight 1: 10x throughput
4. Key Insight 2: C++ audited implementation
5. Opportunity: Early validator operators
6. Implication: Enterprise-grade infrastructure
7. Closing: The L1 wars are over

## LINKEDIN POST:
Solana's Firedancer launch marks a pivotal infrastructure milestone. First production-grade alternative validator client—something no other L1 has achieved. For institutional investors, this represents derisked infrastructure.

END."""

def generate_career() -> str:
    """Career advice response."""
    return """## MATCHED ROLES:
1. Senior Rust Engineer at Phantom
   - Fit: Wallet infrastructure
   - Gap: Mobile development

2. Protocol Engineer at Marinade
   - Fit: Liquid staking expertise
   - Gap: Formal verification

3. Research Analyst at Multicoin
   - Fit: Technical writing
   - Gap: Traditional finance

## POSITIONING:
Frame as Solana-native builder with protocol research skills.

## ACTIONS:
- Contribute to Solana Stack Exchange
- Publish technical analysis on X
- Open-source a Rust tool

END."""

def generate_execution() -> str:
    """Execution/task response."""
    return """## TASK BREAKDOWN:
- Research target company background
- Draft personalized outreach
- Prepare relevant work samples
- Follow up timeline

## OUTPUTS:
Cold outreach email + project README

## MESSAGES:
Subject: Protocol Engineer Application - [Name]

Hi [Name],

I've been following [Company]'s work on [specific project]. Recently built [relevant project] that aligns with your roadmap.

Would love to discuss how I can contribute.

Best,
[Your Name]

## NEXT ACTION:
Send email to hiring manager today.

END."""

def generate_default_research(task: str) -> str:
    """Generate contextual research for unknown topics."""
    return f"""## EXECUTIVE SUMMARY
{task.split()[0] if task else "This topic"} represents a significant area of research within the crypto ecosystem, with unique characteristics that differentiate it from traditional finance and other blockchain implementations.

## PROBLEM IDENTIFICATION
**Current State:**
- Market fragmentation creates inefficiencies
- Information asymmetry between participants
- Technical complexity limiting adoption
- Regulatory uncertainty causing hesitancy

**Root Cause Analysis:**
- Surface: User experience friction and education gaps
- Deep: Protocol design trade-offs (security vs scalability vs decentralization)
- Systemic: Misaligned incentives in early-stage ecosystems

## DATA & EVIDENCE
**Key Metrics:**
| Metric | Value | Trend | Source |
|--------|-------|-------|--------|
| Market Size | $XXB | Growing | Industry Reports |
| Participant Count | XXX | ↑ | On-chain Data |
| Average Transaction | $XXX | Stable | DEX Analytics |
| Growth Rate | XX% | ↑ | YoY Analysis |

## WORKFLOW ANALYSIS
**Current Process:**
```
[Input] → [Process] → [Output]
   ↓         ↓          ↓
[Issue]   [Issue]    [Issue]
```

**Inefficiencies:**
1. Manual processes requiring automation
2. Information silos limiting coordination
3. High barriers to entry for new participants

## SOLUTIONS PROPOSED
**Solution 1: Process Automation**
- Problem: Manual workflows creating delays
- Approach: Smart contract automation
- Timeline: 3-6 months
- Success: 50% efficiency improvement

**Solution 2: Information Integration**
- Problem: Siloed data sources
- Approach: Unified data layer
- Timeline: 6-9 months
- Success: Real-time visibility

**Solution 3: Accessibility Improvements**
- Problem: High barriers to entry
- Approach: Simplified UX and education
- Timeline: 2-4 months
- Success: 3x user growth

## ACTIONABLE ROADMAP
**Immediate (0-7 days):**
- Research current solutions in market
- Identify key stakeholders
- Document current pain points

**Short-term (1-4 weeks):**
- Evaluate existing tools and protocols
- Build proof-of-concept
- Gather user feedback

**Medium-term (1-3 months):**
- Develop production solution
- Launch pilot program
- Iterate based on data

END."""
