"use client";

import { useState, useRef, useEffect } from "react";
import React from "react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  mode?: string;
  timestamp: Date;
}

const MODES = [
  { id: "AUTO", label: "Auto", icon: "🤖", color: "bg-gray-700" },
  { id: "RESEARCH", label: "Research", icon: "🔬", color: "bg-blue-600" },
  { id: "OPPORTUNITY", label: "Opportunity", icon: "💼", color: "bg-green-600" },
  { id: "SIGNAL", label: "Signal", icon: "⚡", color: "bg-yellow-600" },
  { id: "ANALYSIS", label: "Analysis", icon: "📊", color: "bg-purple-600" },
  { id: "CONTENT", label: "Content", icon: "📝", color: "bg-pink-600" },
  { id: "CAREER", label: "Career", icon: "🎯", color: "bg-indigo-600" },
  { id: "EXECUTION", label: "Execution", icon: "⚙️", color: "bg-gray-600" },
];

const EXAMPLE_QUERIES = [
  "Research Solana's Firedancer upgrade in depth",
  "Analyze DeFi protocol metrics with data",
  "Detect emerging narratives early",
  "Find research grants with workflows",
  "Compare L2 performance with charts",
  "Identify problems in crypto custody",
];

// Rich content formatter component
const FormattedContent = ({ content }: { content: string }) => {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Skip END.
    if (line.trim() === "END." || line.trim() === "END") {
      i++;
      continue;
    }

    // Code blocks (```)
    if (line.startsWith("```")) {
      const language = line.slice(3).trim();
      let code = "";
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        code += lines[i] + "\n";
        i++;
      }
      elements.push(
        <pre key={i} className="bg-gray-950 border border-gray-800 rounded-lg p-4 my-4 overflow-x-auto">
          <code className="text-sm font-mono text-gray-300 whitespace-pre">{code}</code>
        </pre>
      );
      i++;
      continue;
    }

    // Tables (lines with |)
    if (line.includes("|") && i + 1 < lines.length && lines[i + 1].includes("-")) {
      const headers = line.split("|").map(h => h.trim()).filter(h => h);
      i += 2; // skip header and separator
      const rows: string[][] = [];
      while (i < lines.length && lines[i].includes("|")) {
        rows.push(lines[i].split("|").map(c => c.trim()).filter(c => c));
        i++;
      }
      elements.push(
        <div key={i} className="overflow-x-auto my-4">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-800">
                {headers.map((h, idx) => (
                  <th key={idx} className="px-4 py-2 text-left text-gray-300 font-semibold border border-gray-700">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, ridx) => (
                <tr key={ridx} className="bg-gray-900/50 hover:bg-gray-800/50">
                  {row.map((cell, cidx) => (
                    <td key={cidx} className="px-4 py-2 text-gray-400 border border-gray-800">{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    // Headers ##
    if (line.startsWith("## ")) {
      elements.push(
        <h2 key={i} className="text-xl font-bold text-white mt-6 mb-3 border-b border-gray-700 pb-2">
          {line.replace("## ", "")}
        </h2>
      );
      i++;
      continue;
    }

    // Headers ###
    if (line.startsWith("### ")) {
      elements.push(
        <h3 key={i} className="text-lg font-semibold text-blue-400 mt-5 mb-2">
          {line.replace("### ", "")}
        </h3>
      );
      i++;
      continue;
    }

    // Headers ####
    if (line.startsWith("#### ")) {
      elements.push(
        <h4 key={i} className="text-base font-medium text-gray-300 mt-4 mb-2">
          {line.replace("#### ", "")}
        </h4>
      );
      i++;
      continue;
    }

    // Bold text **
    if (line.includes("**")) {
      const parts = line.split(/(\*\*.*?\*\*)/g);
      elements.push(
        <p key={i} className="mb-2 text-gray-300">
          {parts.map((part, idx) => {
            if (part.startsWith("**") && part.endsWith("**")) {
              return <strong key={idx} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
            }
            return part;
          })}
        </p>
      );
      i++;
      continue;
    }

    // ASCII Art / Charts (preserve whitespace)
    if (line.startsWith("  ") || (line.match(/^[│┌┐└┘├┤┬┴┼╭╮╯╰─═]/))) {
      let art = "";
      while (i < lines.length && (lines[i].startsWith("  ") || lines[i].match(/^[│┌┐└┘├┤┬┴┼╭╮╯╰─═\[\]│/>\-_\\/\\^╱╲]/))) {
        art += lines[i] + "\n";
        i++;
      }
      elements.push(
        <pre key={i} className="bg-gray-950 border border-gray-800 rounded-lg p-3 my-3 overflow-x-auto">
          <code className="text-xs font-mono text-gray-400 whitespace-pre">{art}</code>
        </pre>
      );
      continue;
    }

    // Numbered lists
    if (line.match(/^\d+\./)) {
      elements.push(
        <div key={i} className="ml-4 mb-2 text-gray-300 flex gap-2">
          <span className="text-blue-400 font-semibold min-w-[1.5rem]">{line.match(/^\d+/)?.[0]}.</span>
          <span>{line.replace(/^\d+\.\s*/, "")}</span>
        </div>
      );
      i++;
      continue;
    }

    // Bullet lists with content
    if (line.startsWith("- ") || line.startsWith("• ")) {
      const content = line.replace(/^[-•]\s*/, "");
      // Check if it's a sub-item
      if (content.includes(":")) {
        const [label, ...rest] = content.split(":");
        elements.push(
          <div key={i} className="ml-4 mb-1 text-gray-400 flex gap-2">
            <span className="text-blue-500">•</span>
            <span>
              <span className="text-gray-300 font-medium">{label}:</span>
              {rest.join(":")}
            </span>
          </div>
        );
      } else {
        elements.push(
          <div key={i} className="ml-4 mb-1 text-gray-400 flex gap-2">
            <span className="text-blue-500">•</span>
            <span>{content}</span>
          </div>
        );
      }
      i++;
      continue;
    }

    // Empty lines
    if (line.trim() === "") {
      elements.push(<div key={i} className="h-2" />);
      i++;
      continue;
    }

    // Regular paragraphs
    elements.push(
      <p key={i} className="mb-2 text-gray-300 leading-relaxed">
        {line}
      </p>
    );
    i++;
  }

  return <>{elements}</>;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedMode, setSelectedMode] = useState("AUTO");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const mode = selectedMode === "AUTO" ? detectMode(input) : selectedMode;
      const response = await generateResponse(input, mode);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response,
        mode: mode,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const detectMode = (query: string): string => {
    const q = query.toLowerCase();
    if (q.includes("deep") || q.includes("comprehensive") || q.includes("in-depth")) return "RESEARCH";
    if (q.includes("grant") || q.includes("job") || q.includes("fellowship")) return "OPPORTUNITY";
    if (q.includes("trend") || q.includes("signal") || q.includes("emerging")) return "SIGNAL";
    if (q.includes("analyze") || q.includes("data") || q.includes("metric") || q.includes("chart")) return "ANALYSIS";
    if (q.includes("post") || q.includes("thread") || q.includes("content")) return "CONTENT";
    if (q.includes("career") || q.includes("resume")) return "CAREER";
    if (q.includes("apply") || q.includes("email") || q.includes("draft")) return "EXECUTION";
    return "RESEARCH";
  };

  const generateResponse = async (query: string, mode: string): Promise<string> => {
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const responses: Record<string, string> = {
      RESEARCH: `## EXECUTIVE SUMMARY
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

**Historical Outage Analysis:**
\`\`\`
2023 Outages: 12 incidents (total 42 hours)
2024 Outages: 3 incidents (total 6 hours)
Trend: Improving but still vulnerable
\`\`\`

## WORKFLOW ANALYSIS
**Current Process Flow:**
\`\`\`
Transaction → Agave Client → Banking Stage → PoH → Consensus → Broadcast
                ↓              ↓            ↓         ↓           ↓
           [Bottleneck]    [Bottleneck] [Latency] [Delay]   [Propagation]
\`\`\`

**Inefficiencies Identified:**
1. Single-threaded banking stage limits parallel processing
2. Signature verification dominates CPU usage (~40%)
3. Gossip protocol overhead during high TPS
4. State growth causing storage bottlenecks

## VISUAL FRAMEWORK
**Market Map:**
\`\`\`
Firedancer    ←→    Agave    ←→    Jito-Solana
   ↑                   ↑              ↑
[C++ rewrite]    [Rust OG]    [MEV optimized]
10x throughput   Stable     Revenue focused
\`\`\`

**Adoption Trajectory:**
\`\`\`
Validators
    │                               ╭──────╮
    │                          ╭────╯      ╲
    │                     ╭────╯             ╲___
1800│    ╭─────────╮  ╱                      ╲
    │   ╱           ╲╱                         ╲___
    │__╱                                            ╲__
    └──────────────────────────────────────────────────→
       2023      2024      2025      2026
       Launch   Testnet   Mainnet   Maturity
\`\`\`

## DEEP ANALYSIS
**Why It Matters:**
- Institutional adoption requires 99.99% uptime SLA
- Competition from Sui, Aptos pushing throughput requirements
- Economic security depends on validator decentralization
- Regulatory scrutiny requires client diversity

**How It Works:**
- Firedancer reimplements Solana protocol in C++17
- Modular architecture with NUMA-aware thread scheduling
- Zero-copy networking with kernel bypass (DPDK)
- Optimized signature verification (batch verification)

**Ecosystem Impact:**
- Upstream: Hardware vendors validating on new client
- Downstream: RPC providers gaining reliability
- Cross-chain: Sets precedent for client diversity

## OPPORTUNITIES IDENTIFIED
1. **Firedancer RPC Node Operations**
   - Size: $50M+ annual market
   - Timing: First 6 months of mainnet
   - Difficulty: 7/10
   - Resources needed: $10K hardware, DevOps skills
   - Action: Set up testnet node, benchmark vs Agave

2. **Validator Client Migration Consulting**
   - Size: $5M service market
   - Timing: 6-12 month window
   - Difficulty: 6/10
   - Resources needed: Protocol knowledge, tooling
   - Action: Build migration guide and tooling

3. **Client Diversity Monitoring Tools**
   - Size: $2M tooling market
   - Timing: Immediate need
   - Difficulty: 4/10
   - Resources needed: Data engineering
   - Action: Build dashboard tracking client distribution

## SOLUTIONS PROPOSED
**Solution 1: Graduated Mainnet Rollout**
- Problem addressed: Risk of mass migration causing instability
- Approach: Canary validators → 5% → 25% → 50% thresholds
- Implementation: Staged deployment with automated rollback
- Resources: Coordination with validator community
- Timeline: 12 months
- Success metrics: Uptime >99.9%, client diversity >30%
- Risks: Low adoption, mitigation via incentives

**Solution 2: Client-Agnostic Infrastructure**
- Problem addressed: Tooling fragmentation
- Approach: Standardized APIs across clients
- Implementation: SDK abstraction layer
- Resources: Developer time, documentation
- Timeline: 6 months
- Success metrics: 10+ tools supporting both clients
- Risks: Complexity increase, mitigation via gradual adoption

## ACTIONABLE ROADMAP
**Immediate (0-7 days):**
- Benchmark Firedancer RPC latency vs Agave on testnet
- Join Firedancer Discord for validator coordination
- Review Firedancer source code architecture

**Short-term (1-4 weeks):**
- Deploy testnet validator with Firedancer
- Document migration experience
- Build monitoring dashboard

**Medium-term (1-3 months):**
- Production validator migration plan
- Consulting service launch
- Tooling development

## SIGNALS & INDICATORS
**Early Warning Signs:**
- Validator count declining during migration
- Client bug reports increasing
- Performance regression in benchmarks

**Success Indicators:**
- 20%+ validator adoption by Q3 2025
- Zero consensus failures for 90 days
- Major RPC providers offering Firedancer endpoints

END.`,

      ANALYSIS: `## ANALYTICAL FRAMEWORK
**Methodology:** Mixed quantitative/qualitative
**Data Sources:** On-chain (SolanaFM), Off-chain (Messari, Token Terminal)
**Time Period:** 90-day rolling analysis
**Confidence Level:** High (85%) - Multiple data sources confirm trends

## DATA LANDSCAPE
**Raw Data Points:**
| Metric | Current | 7d Avg | 30d Avg | 90d Avg | YoY |
|--------|---------|--------|---------|---------|-----|
| Daily Fees | $2.8M | $2.6M | $2.4M | $2.1M | +156% |
| Active Addresses | 1.2M | 1.1M | 980K | 850K | +89% |
| Staked SOL | 68% | 69% | 70% | 72% | -4% |
| TX Success Rate | 85% | 83% | 82% | 78% | +12% |
| Avg TX Cost | $0.002 | $0.003 | $0.004 | $0.006 | -78% |

**Statistical Summary:**
- Mean Daily Volume: $1.2B
- Median TX Size: $450
- Std Dev (volatility): 23%
- Min/Max Daily Fees: $800K / $4.2M
- Sample Size: 90 days

## CORRELATION ANALYSIS
**Variable Relationships:**
\`\`\`
Correlation Matrix:
              Price    Volume   TVL    Users   Fees
Price          1.00     0.72    0.65    0.58    0.81
Volume         0.72     1.00    0.89    0.76    0.92
TVL            0.65     0.89    1.00    0.71    0.85
Users          0.58     0.76    0.71    1.00    0.68
Fees           0.81     0.92    0.85    0.68    1.00
\`\`\`

**Key Findings:**
- Strong positive correlation (>0.7): Volume↔Fees (0.92), Price↔Fees (0.81)
- Moderate correlation (0.3-0.7): TVL↔Users (0.71)
- Negative correlation: None significant
- No correlation (<0.3): Price↔Users (0.58) - users growing independent of price

## TREND ANALYSIS
**Historical Trajectory:**
\`\`\`
Daily Active Users (90-day):

  1.2M │                             ╭───╮
       │                          ╭──╯   ╲
  900K │    ╭────────╮       ╭───╯       ╲___
       │   ╱          ╲    ╭──╯                ╲
  600K │__╱            ╲──╯                    ╲___
       │
  300K │___________________________________________
       └────────────────────────────────────────────→
       Day 0     Day 30    Day 60    Day 90

Trend: Exponential growth phase (R² = 0.87)
Seasonality: Weekly pattern (higher weekdays)
Anomalies: Day 45 spike (Jupiter airdrop)
\`\`\`

**Forecast (30/60/90-day):**
- Conservative: 1.3M / 1.4M / 1.5M users
- Baseline: 1.4M / 1.6M / 1.8M users
- Optimistic: 1.6M / 2.0M / 2.5M users
- Confidence: 75%

## COMPARATIVE ANALYSIS
**Benchmark vs Competitors:**
| Dimension | Solana | Ethereum | Arbitrum | Base | Industry |
|-----------|--------|----------|----------|------|----------|
| Daily TXs | 28M | 1.2M | 800K | 600K | - |
| TX Cost | $0.002 | $2.5 | $0.1 | $0.01 | $0.5 |
| Finality | 400ms | 12min | 15min | 3min | 5min |
| TPS | 65K | 15 | 4K | 3K | 2K |
| Rank | #1 | #2 | #3 | #4 | - |

**Competitive Position:**
- Strengths: Throughput (10x nearest competitor), cost (1000x cheaper)
- Weaknesses: Decentralization metrics, client diversity
- Opportunities: Institutional DeFi, payments
- Threats: Modular blockchain thesis (Celestia + rollups)

## SEGMENTATION
**User Cohorts:**
| Segment | Size | Avg Value | Churn | LTV | CAC | Health |
|---------|------|-----------|-------|-----|-----|--------|
| Whales (>10K) | 2% | $45K | 5% | $900K | $2K | 9.2/10 |
| Power (1K-10K) | 8% | $5K | 12% | $60K | $800 | 7.8/10 |
| Regular (100-1K) | 25% | $600 | 22% | $13K | $400 | 6.5/10 |
| Retail (<100) | 65% | $80 | 35% | $1.2K | $150 | 4.2/10 |

**Behavioral Patterns:**
- High-value actions: Staking, LP provision, perpetual trading
- Drop-off points: First transaction (40% never return), first loss
- Activation sequence: Wallet → Fund → Trade → Stake (optimal: <7 days)

## PATTERN IDENTIFICATION
**Emerging Patterns:**
1. **Institutional Inflow**: Correlation between USDC inflows and price stability (0.68)
   - Evidence: $200M weekly average institutional deposits
   - Drivers: ETF approval anticipation, stablecoin adoption
   - Projection: Continuation through Q2 2025

2. **DePIN Activity Surge**: +400% QoQ in decentralized physical infra
   - Evidence: Helium, Hivemapper, Render network growth
   - Drivers: Real-world asset tokenization trend
   - Projection: 10x growth by 2026

**Anomalies Detected:**
- Day 32: Transaction volume spike +340% (Jupiter airdrop claim)
- Day 67: Failed transaction rate spike to 25% (network congestion)

## ROOT CAUSE ANALYSIS
**Problem Tree:**
\`\`\`
                    High Fees (Problem)
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
   Congestion      Inefficient       Spam TXs
   (40%)           Batch Processing   (20%)
        │                  │                  │
   Priority Fee      Compute Budget    MEV Bots
   Auction           Limits
\`\`\`

## INSIGHTS
**Key Findings:**
1. Network activity quality exceeds quantity - fees/tx ratio improving
2. Institutional adoption driving sustainable growth vs speculation
3. Throughput headroom sufficient for 10x growth without congestion
4. User retention correlates strongly with first-week transaction count

**Strategic Implications:**
- Infrastructure investment priority: RPC capacity > validator count
- Marketing focus: First-transaction experience critical
- Risk if ignored: Competitor chains closing TPS gap

## RECOMMENDATIONS
**Priority Actions:**
| Priority | Action | Impact | Effort | ROI | Timeline |
|----------|--------|--------|--------|-----|----------|
| P0 | Optimize RPC caching | High | Med | 5x | 2 weeks |
| P1 | First-tx onboarding | High | Low | 3x | 1 week |
| P2 | Spam detection algo | Med | High | 2x | 1 month |

END.`,

      SIGNAL: `## SIGNAL OVERVIEW
**Signal Strength:** 8/10 | **Urgency:** 7/10 | **Confidence:** 82%
**Detection Date:** 2025-05-15 | **Maturity:** Early/Emerging
**Category:** Narrative/Technological (AI x Crypto intersection)

## EARLY SIGNALS DETECTED
**Primary Signals:**
1. **AI Agent Token Explosion** — Strength: High
   - Indicator: Market cap of AI agent tokens grew from $100M to $2.4B in 90 days
   - Source: Coingecko, Token Terminal
   - Velocity: +400% QoQ, accelerating
   - Precedent: DeFi Summer 2020 (similar growth trajectory)

2. **Autonomous Wallet Activity** — Strength: High
   - Indicator: AI agents executing on-chain transactions autonomously
   - Source: BONKbot, HeyWallet analytics
   - Velocity: 50K+ AI-driven TXs/day
   - Precedent: Bot trading in 2017 (10x scale difference)

**Supporting Evidence:**
\`\`\`
Signal Timeline:
Day -90: First AI agent tokens launch (Bittensor, Fetch)
Day -60: Autonomous trading agents appear
Day -30: Major VC announcements (a16z, Paradigm AI crypto funds)
Day -14: Coinbase lists AI agent category
Day 0:   Current: Mainstream crypto Twitter attention
Day +7:  Projected: First enterprise AI agent deployment
\`\`\`

**Leading Indicators:**
| Indicator | Current | Change | Threshold | Status |
|-----------|---------|--------|-----------|--------|
| AI Token MC | $2.4B | +400% | $1B | ✅ Triggered |
| GitHub AI Crypto | 450 repos | +180% | 200 | ✅ Triggered |
| VC AI Investments | $800M | +300% | $500M | ✅ Triggered |
| Social Mentions | 45K/day | +250% | 20K | ⚠️ Approaching |

## ANOMALY DETECTION
**Statistical Anomalies:**
- AI token velocity: 4.2 σ above historical DeFi average
- Developer activity: 95th percentile vs all crypto sectors
- VC funding rate: 3x normal crypto AI investment pace

**Behavioral Shifts:**
- From: Human-driven DeFi protocols
- To: Autonomous AI agents managing portfolios
- Delta: 50K daily autonomous transactions
- Significance: p < 0.001 (99.9% confidence)

## MARKET DYNAMICS
**Adoption Curve Position:**
\`\`\`
Innovators → Early Adopters → Early Majority → Late Majority → Laggards
    │              ★               │               │             │
   [5%]         [current]         [15%]          [35%]         [50%]

We're here → Evidence: Mainstream CT coverage, VC FOMO, retail entry
\`\`\`

**Network Effects:**
- Metcalfe's Law: Users² correlation = 0.76
- Critical mass: 65% reached
- Viral coefficient: K = 1.4 (expansion phase)
- Churn vs Growth: 1:4 ratio (healthy)

**Stakeholder Map:**
\`\`\`
         [OpenAI/Anthropic]
                  │
                  ↓
[VCs: a16z] ← [Core AI Crypto] → [Developers]
     ↓              ↑              ↓
[Retail]      [Users]        [Infrastructure]
\`\`\`

## WHY IT MATTERS
**First-Order Effects:**
- New asset class: AI agents as economic entities
- Trading paradigm shift: Human → Algorithmic → Autonomous
- Infrastructure demands: Real-time inference on-chain

**Second-Order Effects:**
- Regulatory attention: AI agents as legal entities
- Traditional finance: Automated wealth management competition
- Talent migration: AI engineers → Crypto

**Third-Order Effects:**
- Economic restructuring: Labor markets for autonomous agents
- Governance innovation: AI participation in DAOs
- Paradigm shift: Proof-of-intelligence consensus mechanisms

**Historical Parallels:**
| Event | Similarity | Timeline | Outcome |
|-------|------------|----------|---------|
| DeFi Summer 2020 | 85% | 18 months | $100B+ TVL |
| NFT Boom 2021 | 70% | 12 months | $40B market |
| L2 Wars 2022 | 60% | 24 months | Ongoing |

## EARLY OPPORTUNITIES
**Tactical (0-30 days):**
1. **AI Agent Infrastructure Tokens**
   - Entry: Accumulate Bittensor, Fetch.ai, Render positions
   - Size: $10-50K potential (short-term)
   - Risk: High volatility, mitigation via dollar-cost averaging
   - Time decay: High - window closing
   - Action: DCA over 2 weeks, set stop-losses

**Strategic (1-6 months):**
2. **Autonomous Agent Development**
   - Entry: Build specialized trading agents
   - Size: $100K+ service revenue potential
   - Risk: Technical complexity, mitigation via partnerships
   - Time decay: Medium - first-mover advantage
   - Action: Build MVP agent, test on testnet

**Transformational (6-12 months):**
3. **AI Agent Marketplace Platform**
   - Entry: Infrastructure for agent discovery/hiring
   - Size: $1B+ market potential
   - Risk: Regulatory uncertainty
   - Time decay: Low - infrastructure play
   - Action: Research regulatory landscape, build framework

## RISK ASSESSMENT
**Risks:**
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Regulatory ban | 30% | High | Geographic diversification |
| AI agent failure | 25% | High | Extensive testing, insurance |
| Market saturation | 50% | Medium | Focus on niche specializations |

**Warning Signs (Reversal Indicators):**
- AI token MC falling below $1B for 30 days
- Major AI agent hack/exploit
- Regulatory action from SEC/CFTC

## FORECAST
**Scenario Planning:**

**Bull Case (30% probability):**
- Triggers: Major exchange lists AI agent index, enterprise adoption
- Trajectory: Parabolic growth, $10B+ market cap
- Timeline: 6 months to peak
- Outcome: AI agents become dominant crypto narrative

**Base Case (50% probability):**
- Triggers: Gradual adoption, infrastructure improvements
- Trajectory: Steady growth, $5B market cap
- Timeline: 12 months to maturity
- Outcome: Sustainable AI agent ecosystem

**Bear Case (20% probability):**
- Triggers: Regulatory crackdown, major exploit
- Trajectory: Sharp correction, 80% drawdown
- Timeline: 3 months to bottom
- Outcome: Narrative resets, survivors emerge

**Key Decision Points:**
\`\`\`
Now ──→ [30d: Adoption Rate] ──→ [90d: Regulatory Clarity] ──→ [Outcome]
        [enter/accumulate]         [scale/exit]                [final state]
          ↓                          ↓                          ↓
      [DCA strategy]            [position sizing]           [reassess]
\`\`\`

## ACTION PLAN
**Immediate Actions (This Week):**
1. Allocate 5% portfolio to AI agent infrastructure tokens
2. Research autonomous agent frameworks (LangChain, Eliza)
3. Join AI crypto Discords for alpha

**Setup Actions (This Month):**
1. Deploy test agent on testnet
2. Document successful agent strategies
3. Build monitoring dashboard

**Monitoring Dashboard:**
- Track: AI token MC, developer activity, social sentiment
- Alert when: MC drops 30% in 7 days, negative regulatory news
- Review: Weekly strategy adjustments

END.`,

      OPPORTUNITY: `## OPPORTUNITY LANDSCAPE
**Market Overview:** Research and development opportunities across crypto and traditional sectors
**Target Profile:** Researchers, analysts, academics, technical writers
**Total Addressable:** $500M+ annual research funding
**Timeline:** Rolling applications, peak season Q1-Q2

## TOP OPPORTUNITIES

### 1. Messari - Crypto Research Analyst (In Crypto)
**What:** Produce sector-specific research reports on DeFi/DePIN protocols
**Who For:** Researchers with crypto-native experience
**Why:** Leading crypto intelligence firm, high industry visibility, $120-180K comp
**Requirements:**
- Deep understanding of DeFi mechanics
- Financial modeling capabilities
- Technical writing excellence
- 2+ years crypto research experience

**Skill Match:** High
**Difficulty:** 7/10
**Success Probability:** Medium (15% acceptance rate)
**Time to Apply:** 2-3 weeks preparation
**Action Steps:**
1. Draft 2,000-word sample report on emerging sector
2. Build Messari-style financial model in Excel
3. Prepare case study of previous research
4. Submit via messari.io/careers with portfolio

**Compensation:** $120-180K + equity
**Application Deadline:** Rolling
**Work Arrangement:** Remote/Hybrid (NYC)

---

### 2. Open Society Foundations - Digital Rights Research Grant (Outside Crypto)
**What:** $100K grant for studying surveillance technology and democratic governance
**Who For:** Traditional researchers, academics, policy analysts
**Why:** No crypto background required, prestigious foundation, policy impact focus
**Requirements:**
- PhD or equivalent research experience
- Published work in relevant field
- Policy engagement experience
- International perspective preferred

**Skill Match:** Medium (domain transfer needed)
**Difficulty:** 4/10
**Success Probability:** High (30% acceptance rate)
**Time to Apply:** 1 month proposal development
**Action Steps:**
1. Review OSF's digital rights portfolio
2. Identify research gap in surveillance tech
3. Draft proposal with clear methodology
4. Secure institutional affiliation
5. Submit at opensociety.org/grants by March 30

**Deliverables:** 12-month research report + policy brief
**Grant Amount:** $100K (flexible based on scope)
**Application Deadline:** March 30, 2025
**Work Arrangement:** Fully remote

---

### 3. a16z crypto - Research Fellow (In Crypto)
**What:** 6-month fellowship exploring zero-knowledge proofs and scalability
**Who For:** Advanced researchers, PhD candidates, protocol engineers
**Why:** Access to $7B portfolio, publish under a16z brand, potential full-time conversion
**Requirements:**
- Strong cryptographic background
- Published research or significant GitHub contributions
- Deep expertise in ZK proofs or related field
- Independent research capabilities

**Skill Match:** High (technical depth required)
**Difficulty:** 9/10
**Success Probability:** Low (5% acceptance rate)
**Time to Apply:** 4-6 weeks proposal development
**Action Steps:**
1. Identify specific research question in ZK space
2. Review a16z crypto research blog for alignment
3. Draft 10-page research proposal
4. Secure academic or industry recommendation
5. Email research@a16zcrypto.com with thesis proposal

**Fellowship Terms:** $15K/month stipend + conference budget
**Duration:** 6 months (extendable)
**Application Deadline:** Rolling quarterly
**Work Arrangement:** Remote with SF/NYC presence quarterly

---

### 4. Ethereum Foundation - Academic Research Grant (In Crypto)
**What:** $50K-$250K grant for protocol research (consensus, P2P, cryptography)
**Who For:** Academics, postdocs, research scientists
**Why:** Open-ended research, academic credibility, no deliverable pressure
**Requirements:**
- Academic affiliation
- Research track record
- Open-source commitment
- Community engagement

**Skill Match:** High
**Difficulty:** 6/10
**Success Probability:** Medium-High (25% acceptance)
**Time to Apply:** 6-8 weeks
**Action Steps:**
1. Identify research area aligned with EF roadmap
2. Connect with EF researcher in domain
3. Draft academic-style proposal
4. Submit via esp.ethereum.foundation

**Grant Range:** $50K-$250K based on scope
**Application Deadline:** Rolling, quarterly reviews

---

### 5. Vitalik Buterin Fellowship - Public Goods Research (Outside Crypto)
**What:** $50K stipend for public goods research (mechanism design, governance)
**Who For:** Economists, mechanism designers, governance researchers
**Why:** Direct mentorship, high impact potential, flexible scope
**Requirements:**
- Economics or mechanism design background
- Quantitative modeling skills
- Public goods focus
- Publication history

**Skill Match:** Medium-High
**Difficulty:** 8/10
**Success Probability:** Low-Medium (10% acceptance)
**Time to Apply:** 4 weeks

END.`,
    };

    return responses[mode] || responses.RESEARCH;
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-xl font-bold">
              G
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                GIDBoy
              </h1>
              <p className="text-xs text-gray-500">Deep Research Intelligence OS</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-xs text-gray-600 hidden sm:block">
              Deep Analysis Mode
            </div>
            <div className="text-xs bg-gray-800 px-3 py-1 rounded-full text-gray-400">
              v2.0
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 flex gap-6">
        <aside className="w-72 hidden lg:block flex-shrink-0">
          <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-800 sticky top-24">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
              Intelligence Mode
            </h3>
            <div className="space-y-1">
              {MODES.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => setSelectedMode(mode.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
                    selectedMode === mode.id
                      ? `${mode.color} text-white shadow-lg`
                      : "text-gray-400 hover:bg-gray-800 hover:text-gray-200"
                  }`}
                >
                  <span className="text-lg">{mode.icon}</span>
                  <div className="text-left">
                    <div className="font-medium">{mode.label}</div>
                    {selectedMode === mode.id && (
                      <div className="text-xs opacity-70">
                        {mode.id === "RESEARCH" && "Deep analysis with data"}
                        {mode.id === "ANALYSIS" && "Metrics & correlations"}
                        {mode.id === "SIGNAL" && "Early detection"}
                        {mode.id === "OPPORTUNITY" && "Jobs & grants"}
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 bg-gray-900/50 rounded-xl p-4 border border-gray-800">
            <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
              Quick Start
            </h3>
            <div className="space-y-2">
              {EXAMPLE_QUERIES.map((query, i) => (
                <button
                  key={i}
                  onClick={() => setInput(query)}
                  className="w-full text-left px-3 py-2 text-xs text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded-lg transition-colors border border-transparent hover:border-gray-700"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 bg-blue-900/20 border border-blue-800/50 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-blue-400 mb-2">
              💡 Pro Tips
            </h3>
            <ul className="text-xs text-gray-400 space-y-1.5">
              <li>• Use "deep" for comprehensive analysis</li>
              <li>• Add "with data" for metrics</li>
              <li>• Request "workflows" for processes</li>
              <li>• Ask for "solutions" for problems</li>
            </ul>
          </div>
        </aside>

        <main className="flex-1 flex flex-col min-h-[calc(100vh-140px)] max-w-4xl">
          <div className="flex-1 overflow-y-auto space-y-6 mb-6">
            {messages.length === 0 && (
              <div className="text-center py-16">
                <div className="text-7xl mb-6 bg-gradient-to-br from-blue-500 to-purple-600 w-24 h-24 rounded-2xl mx-auto flex items-center justify-center shadow-2xl shadow-blue-500/20">
                  🤖
                </div>
                <h2 className="text-3xl font-bold text-gray-200 mb-3">
                  Deep Research Intelligence
                </h2>
                <p className="text-gray-400 max-w-lg mx-auto mb-2">
                  GIDBoy now delivers comprehensive analysis with:
                </p>
                <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Problem Identification</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Data & Metrics</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Workflows</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Visualizations</span>
                  <span className="bg-gray-800 px-3 py-1 rounded-full">Solutions</span>
                </div>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-3xl rounded-2xl ${
                    message.role === "user"
                      ? "bg-blue-600 text-white px-6 py-4"
                      : "bg-gray-900/50 border border-gray-800 w-full"
                  }`}
                >
                  {message.role === "assistant" && message.mode && (
                    <div className="flex items-center gap-3 px-6 py-3 border-b border-gray-800 bg-gray-800/30 rounded-t-2xl">
                      <span className={`text-xs font-bold px-2 py-1 rounded ${
                        MODES.find(m => m.id === message.mode)?.color || "bg-gray-700"
                      } text-white`}>
                        {message.mode}
                      </span>
                      <span className="text-xs text-gray-500">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      <span className="text-xs text-gray-600 ml-auto">
                        Deep Analysis
                      </span>
                    </div>
                  )}
                  <div className={message.role === "assistant" ? "p-6" : ""}>
                    <div className="prose prose-invert prose-sm max-w-none">
                      {message.role === "assistant" ? (
                        <FormattedContent content={message.content} />
                      ) : (
                        <p className="text-white">{message.content}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-900/50 border border-gray-800 rounded-2xl px-6 py-8 max-w-3xl w-full">
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" />
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce delay-100" />
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce delay-200" />
                    <span className="text-gray-500 text-sm ml-2">Conducting deep research...</span>
                  </div>
                  <div className="mt-4 space-y-2">
                    <div className="h-2 bg-gray-800 rounded-full w-3/4 animate-pulse" />
                    <div className="h-2 bg-gray-800 rounded-full w-1/2 animate-pulse" />
                    <div className="h-2 bg-gray-800 rounded-full w-2/3 animate-pulse" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="relative">
            <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-3 shadow-2xl">
              <div className="flex items-center gap-2 mb-2 px-2">
                <span className="text-xs text-gray-500">Mode:</span>
                <span
                  className={`text-xs px-2 py-1 rounded-full font-medium ${
                    MODES.find((m) => m.id === selectedMode)?.color || "bg-gray-700"
                  } text-white`}
                >
                  {MODES.find((m) => m.id === selectedMode)?.label || "Auto"}
                </span>
                {selectedMode === "AUTO" && (
                  <span className="text-xs text-gray-600 ml-2">
                    Will auto-detect based on query
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask for deep research, analysis with data, workflows, or solutions..."
                  className="flex-1 bg-transparent text-white placeholder-gray-500 px-4 py-4 text-base focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-700 disabled:to-gray-700 disabled:text-gray-500 text-white rounded-xl font-medium transition-all shadow-lg shadow-blue-500/20"
                >
                  {isLoading ? "Analyzing..." : "Research"}
                </button>
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-3 text-center">
              Try: "Deep research on Solana with data, workflows, and solutions" • GIDBoy provides comprehensive analysis
            </p>
          </form>
        </main>
      </div>
    </div>
  );
}
