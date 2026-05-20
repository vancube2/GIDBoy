# GIDBoy Intelligence OS

**Collaborative research and opportunity intelligence system.**

*Last deployed: 2026-05-20*

GIDBoy is NOT a chatbot. It is a collaborative intelligence operating system designed to:
- Perform deep research with structured reasoning
- Investigate complex problems iteratively
- Generate hypotheses and compare explanations
- Detect real-world opportunities
- Identify who benefits from research
- Convert intelligence into content and positioning
- Assist with applications and execution

## 🎯 Philosophy

GIDBoy operates on a **process-driven intelligence** model:

```
question
→ clarify
→ map context
→ investigate
→ generate hypotheses
→ compare possibilities
→ identify opportunities
→ generate strategic implications
→ generate positioning/content
→ suggest next research directions
```

**Never:**
- Generate shallow AI-demo outputs
- Produce instant polished answers
- Hallucinate confidence
- Optimize for sounding intelligent

**Always:**
- Think before concluding
- Explore multiple explanations
- Identify missing information
- Distinguish assumptions from facts
- Connect research to opportunities

## 🏗️ Architecture

```
GIDBoy/
├── agents/                    # Specialized intelligence agents
│   ├── base_agent.py         # Base agent class
│   ├── research_agent.py     # Deep investigation
│   ├── opportunity_agent.py  # Opportunity discovery
│   ├── content_agent.py      # Content generation
│   ├── memory_agent.py       # Long-term memory
│   └── execution_agent.py    # Action planning
│
├── workflows/                 # LangGraph orchestration
│   └── research_workflow.py # Multi-agent pipeline
│
├── prompts/                   # System prompts
│   ├── system.md
│   ├── research_engine.md
│   ├── opportunity_engine.md
│   ├── content_engine.md
│   ├── memory_engine.md
│   └── execution_engine.md
│
├── memory/                    # Vector database
│   └── vector_store.py       # ChromaDB implementation
│
├── api/                       # FastAPI server
│   └── server.py
│
└── database/                  # PostgreSQL persistence
```

## 🚀 Quick Start

### Option 1: Demo Mode (No Setup Required)
```bash
pip install -r requirements.txt
python api/server.py
```

### Option 2: With Ollama (Local LLM)
```bash
# Install Ollama: https://ollama.com
ollama pull llama3.2

USE_OLLAMA=1 python api/server.py
```

### Option 3: With Groq (Cloud)
```bash
# Get free API key: https://console.groq.com (1M tokens/day)
export GROQ_API_KEY=gsk_your_key
python api/server.py
```

## 🧪 Usage

### Full Research Workflow
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "research Solana L2 landscape",
    "mode": "research",
    "deep_mode": true
  }'
```

**Returns:**
- Deep research analysis
- Identified opportunities
- Generated content (threads, posts)
- Execution plan

### Quick Research
```bash
curl -X POST http://localhost:8000/research/quick \
  -H "Content-Type: application/json" \
  -d '{"query": "what is MEV?"}'
```

### Discover Opportunities
```bash
curl -X POST http://localhost:8000/opportunities \
  -H "Content-Type: application/json" \
  -d '{
    "query": "find grants for researchers",
    "research_summary": {...}
  }'
```

### Search Memory
```bash
curl "http://localhost:8000/memory/search?query=solana&n=3"
```

## 🧠 Agent System

### Research Agent
**Process:**
1. Problem understanding
2. Context mapping
3. Evidence gathering
4. Hypothesis generation (multiple)
5. Contradiction analysis
6. Solution exploration
7. Strategic implications

**Output:** Structured research with executive summary, findings, hypotheses, uncertainties

### Opportunity Agent
**Discovers:**
- Crypto-native jobs
- Protocol grants
- DAOs and communities
- Fellowships
- Research positions
- Consulting angles

**Output:** Prioritized opportunities with relevance, requirements, action steps

### Content Agent
**Generates:**
- X/Twitter threads (8-12 tweets)
- LinkedIn posts
- Intelligence briefs
- Research reports

**Output:** Publication-ready content

### Execution Agent
**Assists with:**
- Outreach templates
- Grant proposals
- Application strategies
- Positioning materials

**Output:** Action plans and ready-to-use templates

### Memory Agent
**Manages:**
- Long-term research storage
- Context retrieval
- Pattern detection
- Cross-research connections

## 🔬 Research Process

Every research task follows this mandatory process:

1. **Problem Understanding**
   - What is the actual question?
   - Why does it matter?
   - Who is affected?
   - What assumptions exist?

2. **Context Mapping**
   - What systems are involved?
   - What technologies matter?
   - What market dynamics?
   - What historical context?

3. **Investigation**
   - Gather evidence
   - Compare explanations
   - Identify contradictions
   - Analyze incentives

4. **Hypotheses**
   - Generate multiple hypotheses
   - Do NOT prematurely collapse

5. **Solutions & Implications**
   - Propose solutions
   - Analyze tradeoffs
   - Identify risks

6. **Opportunity Discovery**
   - Identify who may value this research
   - Explain why they should care
   - Define positioning angle

7. **Content & Positioning**
   - Convert to authority-building content
   - Strategic positioning recommendations

8. **Next Directions**
   - Suggest follow-up research
   - Identify open questions

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI |
| Agents | LangGraph |
| Vector DB | ChromaDB |
| LLM | Groq / Ollama / Demo |
| Memory | JSON + ChromaDB |
| Deployment | GitHub Pages (UI), Vercel (API) |

## 📝 Environment Variables

```bash
# LLM Provider (choose one)
USE_OLLAMA=1                          # Use local Ollama
OLLAMA_URL=http://localhost:11434    # Ollama endpoint

GROQ_API_KEY=gsk_xxx                  # Groq API key

# Optional
CHROMA_PERSIST_DIR=./data/chroma_db  # Vector DB location
PORT=8000                           # API port
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | System info |
| `/health` | GET | Health check |
| `/research` | POST | Full workflow |
| `/research/quick` | POST | Research only |
| `/opportunities` | POST | Opportunity discovery |
| `/memory/search` | GET | Search memory |
| `/memory/stats` | GET | Memory stats |
| `/agents` | GET | List agents |

## 🎓 Thinking Architecture

GIDBoy must NOT function like: `prompt → answer`

Instead it must function like:
```
question
→ clarify
→ map context
→ investigate
→ generate hypotheses
→ compare possibilities
→ identify opportunities
→ generate strategic implications
→ generate positioning/content
→ suggest next research directions
```

This process is **mandatory**.

## 🤝 Contributing

GIDBoy is designed to be modular and extensible. To add a new agent:

1. Create agent in `agents/`
2. Inherit from `BaseAgent`
3. Implement `process()` method
4. Add to workflow in `workflows/research_workflow.py`

## 📄 License

MIT
