"""LLM-based intelligent routing for GIDBoy."""
import os
import json
from typing import Tuple, Optional
from llm_client import call_llm_api

# Mode definitions with detailed descriptions
MODE_DEFINITIONS = {
    "RESEARCH": {
        "description": "Deep research and analysis of crypto topics, protocols, technologies, or ecosystems. Use for: learning, understanding, deep dives, explanations, landscape overviews.",
        "examples": ["research solana L2 landscape", "explain how firedancer works", "what is MEV?", "study DePIN protocols"]
    },
    "OPPORTUNITY": {
        "description": "Finding jobs, grants, funding, fellowships, bounties, stipends, research positions, or career opportunities in crypto and academia.",
        "examples": ["find grants for researchers", "jobs in DeFi", "fellowships for PhD students", "bounties available"]
    },
    "SIGNAL": {
        "description": "Detecting early trends, emerging narratives, alpha signals, market movements, or new developments before they become mainstream.",
        "examples": ["detect new DeFi trends", "what narratives are emerging?", "early signals in AI crypto", "trending sectors"]
    },
    "ANALYSIS": {
        "description": "Data-driven analysis, metrics evaluation, on-chain analysis, pattern identification, statistical review, or performance comparison.",
        "examples": ["analyze solana fee trends", "compare TVL across chains", "on-chain metrics for ETH", "data analysis"]
    },
    "CONTENT": {
        "description": "Creating content like X threads, LinkedIn posts, blog articles, newsletters, video scripts, or podcast outlines.",
        "examples": ["write thread about firedancer", "LinkedIn post about ZK proofs", "newsletter on DePIN", "blog article"]
    },
    "CAREER": {
        "description": "Career advice, resume review, skill development, positioning strategy, interview prep, or professional growth guidance.",
        "examples": ["career advice for researchers", "improve my resume", "what skills should I learn?", "position myself for DeFi roles"]
    },
    "EXECUTION": {
        "description": "Task execution, drafting emails, outreach messages, application materials, proposals, or concrete actionable tasks.",
        "examples": ["draft outreach email", "write grant application", "apply to this job", "send message to founder"]
    }
}


ROUTING_PROMPT = """You are GIDBoy's intent classifier. Your job is to analyze the user's query and determine which of the 7 modes is most appropriate.

AVAILABLE MODES:
{mode_descriptions}

CLASSIFICATION RULES:
1. Analyze the user's intent, not just keywords
2. Consider what the user actually wants to achieve
3. Choose the SINGLE most appropriate mode
4. If multiple modes could fit, pick the one that best matches the PRIMARY intent

OUTPUT FORMAT:
Return ONLY a JSON object with this structure:
{{
    "mode": "MODE_NAME",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of why this mode was chosen",
    "extracted_query": "the clean query without mode prefixes"
}}

USER QUERY: "{query}"

RESPOND WITH JSON ONLY:"""


def build_mode_descriptions() -> str:
    """Build mode descriptions for the routing prompt."""
    descriptions = []
    for mode, info in MODE_DEFINITIONS.items():
        desc = f"\n{mode}:\n  Description: {info['description']}\n  Examples: {', '.join(info['examples'][:2])}"
        descriptions.append(desc)
    return '\n'.join(descriptions)


def llm_route(query: str) -> Tuple[str, str]:
    """Route query using LLM-based intent classification.

    Returns: (mode, clean_query)
    """
    # Check for explicit mode prefix first
    explicit = _check_explicit_mode(query)
    if explicit:
        return explicit

    # Build routing prompt
    mode_desc = build_mode_descriptions()
    prompt = ROUTING_PROMPT.format(
        mode_descriptions=mode_desc,
        query=query
    )

    # Call LLM for classification
    try:
        response = call_llm_api(
            prompt=prompt,
            model="llama-3.1-8b-instant",  # Fast and cheap for routing
            temperature=0.1,
            max_tokens=200
        )

        # Parse JSON response
        result = _parse_routing_response(response)
        if result:
            mode = result.get("mode", "RESEARCH").upper()
            clean_query = result.get("extracted_query", query)

            # Validate mode
            if mode not in MODE_DEFINITIONS:
                mode = "RESEARCH"

            return mode, clean_query

    except Exception as e:
        print(f"LLM routing failed: {e}, falling back to keyword routing")

    # Fallback to keyword routing
    return keyword_route(query)


def _check_explicit_mode(query: str) -> Optional[Tuple[str, str]]:
    """Check for explicit /MODE prefix."""
    import re
    explicit = re.match(r"^/(research|opportunity|signal|analysis|content|career|execution)\s+(.+)", query, re.IGNORECASE)
    if explicit:
        return explicit.group(1).upper(), explicit.group(2).strip()
    return None


def _parse_routing_response(response: str) -> Optional[dict]:
    """Parse the LLM routing response."""
    import re

    # Try to find JSON in the response
    try:
        # Look for JSON block
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        # Try direct parsing
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Fallback: try to extract mode from text
    response_upper = response.upper()
    for mode in MODE_DEFINITIONS.keys():
        if mode in response_upper:
            return {
                "mode": mode,
                "confidence": 0.7,
                "reasoning": "Extracted from text response",
                "extracted_query": response
            }

    return None


def keyword_route(query: str) -> Tuple[str, str]:
    """Fallback keyword-based routing."""
    import re

    q = query.lower().strip()

    keywords = {
        "RESEARCH": ["research", "study", "learn", "explain", "what is", "how does", "deep dive", "overview", "understand"],
        "OPPORTUNITY": ["job", "jobs", "grant", "grants", "dao", "bounty", "bounties", "funding", "hiring", "career", "position", "role", "fellowship", "stipend", "researcher"],
        "SIGNAL": ["signal", "trend", "emerging", "alpha", "early", "detect", "whats new", "narrative", "hype", "attention"],
        "ANALYSIS": ["analyze", "analysis", "data", "pattern", "metrics", "chart", "compare", "performance", "stats", "tvl", "volume", "price"],
        "CONTENT": ["post", "thread", "tweet", "linkedin", "content", "write", "draft", "viral", "blog", "article", "video"],
        "CAREER": ["career", "resume", "cv", "hire", "interview", "skills", "profile", "portfolio"],
        "EXECUTION": ["apply", "email", "draft", "send", "execute", "submit", "reach out", "message", "contact"],
    }

    scores = {}
    for mode, kws in keywords.items():
        score = 0
        for kw in kws:
            if len(kw) <= 4:
                score += 1 if kw in q else 0
            else:
                score += len(re.findall(r'\b' + re.escape(kw) + r'\b', q))
        scores[mode] = score

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "RESEARCH", query


if __name__ == "__main__":
    # Test routing
    test_queries = [
        "research solana L2 landscape",
        "find grants for AI researchers",
        "detect new trends in DeFi",
        "analyze ETH price data",
        "write a thread about ZK proofs",
        "career advice for blockchain devs",
        "draft an email to apply for this grant",
        "what is MEV and how does it work?",
        "compare TVL across major DEXs",
    ]

    print("Testing LLM-based routing:\n")
    for query in test_queries:
        mode, clean = llm_route(query)
        print(f"Query: {query}")
        print(f"→ Mode: {mode}")
        print(f"→ Clean: {clean}\n")
