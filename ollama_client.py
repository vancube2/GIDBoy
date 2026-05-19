import requests
import json
import os
from typing import Optional

OLLAMA_URL = "http://localhost:11434/api/generate"

# Demo responses for when Ollama is not available
DEMO_RESPONSES = {
    "RESEARCH": """INSIGHTS:
- Solana's Firedancer client is entering mainnet beta in Q1 2025
- Jito's MEV infrastructure now processes 80% of Solana transactions
- Institutional custody solutions (Fireblocks, Copper) expanded Solana support

ANALYSIS:
- Why: Network reliability concerns drove validator client diversification
- How: Firedancer uses C++ rewrite for 10x throughput improvement
- Impact: Solana becomes enterprise-grade infrastructure

OPPORTUNITIES:
1. Firedancer RPC node operators - early positioning for validator business
2. Jito restaking derivatives - liquid staking yield optimization
3. Institutional DeFi bridges - compliance-first lending protocols

SIGNALS:
- Coinbase institutional custody quietly added SPL token support

ACTIONS:
- Benchmark Firedancer RPC latency vs Agave
- Research JitoSOL integrations for DeFi protocols

END.""",

    "OPPORTUNITY": """TOP OPPORTUNITIES:

1. Messari - Crypto Research Analyst
   - What: Produce sector-specific research reports on DeFi/DePIN
   - Who For: Researchers (in crypto)
   - Why: Leading crypto intelligence firm, high visibility
   - Skill Match: high
   - Difficulty: 7
   - Action: Submit writing sample via messari.io/careers

2. Open Society Foundations - Digital Rights Research Grant
   - What: $100K grant for studying surveillance tech and democracy
   - Who For: Researchers (outside crypto)
   - Why: No crypto background required, focuses on policy/impact
   - Skill Match: medium
   - Difficulty: 4
   - Action: Apply at opensociety.org/grants by March 30

3. a16z crypto - Research Fellow
   - What: 6-month fellowship exploring cryptographic primitives
   - Who For: Researchers (in crypto)
   - Why: Access to portfolio companies, publish under a16z brand
   - Skill Match: high
   - Difficulty: 9
   - Action: Email research@a16zcrypto.com with thesis proposal

END.""",


    "SIGNAL": """SIGNALS:
1. AI agent tokens on Solana up 400% QoQ with real usage metrics
2. PayPal USD stablecoin volume shifting to Solana from Ethereum
3. Institutional validators increasing stake weight significantly

WHY IT MATTERS:
- Real transaction volume, not speculation
- Payment rails choosing Solana for cost/speed
- Validator decentralization improving

EARLY OPPORTUNITIES:
1. AI x DeFi infrastructure plays
2. Payment SDK integrations
3. Institutional validator tooling

END.""",

    "ANALYSIS": """DATA POINTS:
- Solana daily fees: $2.8M (7-day avg)
- Active addresses: 1.2M (90-day high)
- Staked SOL ratio: 68% (decreasing, indicating utilization)

PATTERNS:
- Fee revenue inversely correlated with spam transactions
- Address growth outpacing Ethereum L2s

INSIGHT:
Network activity is quality-driven, not airdrop farming.

IMPLICATIONS:
- Sustainable revenue for validators
- Real user adoption vs mercenary capital

END.""",

    "CONTENT": """X THREAD:
1. Hook: Solana just did something Ethereum couldn't in 8 years
2. Context: Firedancer validator client hit mainnet
3. Key Insight 1: 10x throughput with same hardware
4. Key Insight 2: Written in C++, audited by 3 firms
5. Opportunity: Early validator node operators
6. Implication: Solana is now enterprise-grade infra
7. Closing: The L1 wars are over. Solana won.

LINKEDIN POST:
Solana's Firedancer client launch marks a pivotal moment for blockchain infrastructure. After years of client diversity challenges, Solana now has a production-grade alternative validator implementation—something no other L1 has achieved. For institutional investors, this represents derisked infrastructure worth evaluating.

END.""",

    "CAREER": """MATCHED ROLES:
1. Senior Rust Engineer at Phantom
   - Fit: Wallet infrastructure, high growth
   - Gap: Mobile development experience

2. Protocol Engineer at Marinade
   - Fit: Liquid staking, DeFi expertise
   - Gap: Formal verification knowledge

3. Research Analyst at Multicoin
   - Fit: Technical writing, ecosystem knowledge
   - Gap: Traditional finance background

POSITIONING:
Frame as Solana-native builder with protocol research skills.

ACTIONS:
- Contribute to Solana Stack Exchange
- Publish technical analysis on X
- Open-source a small Rust tool

END.""",

    "EXECUTION": """TASK BREAKDOWN:
- Research target company background
- Draft personalized outreach
- Prepare relevant work samples
- Follow up timeline

OUTPUTS:
Cold outreach email + project README

MESSAGES:
Subject: Protocol Engineer Application - [Your Name]

Hi [Name],

I've been following [Company]'s work on [specific project]. Recently built [relevant project] that aligns with your roadmap.

Would love to discuss how I can contribute.

Best,
[Your Name]

NEXT ACTION:
Send email to hiring manager today.

END."""
}

def call_ollama(
    prompt: str,
    model: str = "deepseek-r1",
    temperature: float = 0.1,
    timeout: int = 120
) -> str:
    """Call Ollama with fallback to demo mode."""

    # Check if demo mode
    if os.environ.get("GIDBOY_DEMO", "0") == "1":
        # Extract mode from prompt - look for MODE: XXX pattern
        import re
        mode_match = re.search(r"MODE:\s*(\w+)", prompt)
        if mode_match:
            detected_mode = mode_match.group(1).upper()
            if detected_mode in DEMO_RESPONSES:
                return DEMO_RESPONSES[detected_mode]
        return DEMO_RESPONSES["RESEARCH"]

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