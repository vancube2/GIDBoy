import re

def route(query: str):
    """Route query to appropriate mode. Returns (mode, clean_query)."""
    q = query.lower().strip()

    # Explicit mode: /MODE query
    explicit = re.match(r"^/(research|opportunity|signal|analysis|content|career|execution)\s+(.+)", q, re.IGNORECASE)
    if explicit:
        return explicit.group(1).upper(), explicit.group(2).strip()

    # Keyword scoring - use word boundaries for better matching
    keywords = {
        "RESEARCH": ["research", "study", "learn", "explain", "what is", "how does", "deep dive", "overview", "understand"],
        "OPPORTUNITY": ["job", "jobs", "grant", "grants", "dao", "bounty", "bounties", "funding", "hiring", "career", "position", "role", "fellowship", "fellowships", "stipend", "stipends", "researcher", "researchers"],
        "SIGNAL": ["signal", "trend", "emerging", "alpha", "early", "detect", "whats new", "narrative", "narratives", "hype", "attention"],
        "ANALYSIS": ["analyze", "analysis", "data", "pattern", "patterns", "metrics", "chart", "compare", "performance", "stats", "statistical", "tvl", "volume", "price"],
        "CONTENT": ["post", "thread", "tweet", "linkedin", "content", "write", "draft", "viral", "blog", "article", "video", "podcast"],
        "CAREER": ["career", "resume", "cv", "hire", "interview", "skills", "profile", "portfolio"],
        "EXECUTION": ["apply", "email", "draft", "send", "execute", "submit", "reach out", "message", "contact"],
    }

    # Score with word boundary matching
    scores = {}
    for mode, kws in keywords.items():
        score = 0
        for kw in kws:
            # Check if keyword appears as whole word or substring for short words
            if len(kw) <= 4:
                score += 1 if kw in q else 0
            else:
                # For longer keywords, check word boundaries
                score += len(re.findall(r'\b' + re.escape(kw) + r'\b', q))
        scores[mode] = score

    best = max(scores, key=scores.get)

    return best if scores[best] > 0 else "RESEARCH", query