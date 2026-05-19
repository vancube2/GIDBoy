# GIDBoy

Autonomous crypto research and opportunity intelligence agent.

## Features

- **7 Intelligence Modes**: Research, Opportunity, Signal, Analysis, Content, Career, Execution
- **Smart Routing**: Automatic mode detection based on query intent
- **Persistent Memory**: Remembers past research and patterns
- **Dual Targeting**: Opportunities for both crypto-native and traditional researchers

## Quick Start

### Local (with Ollama)

```bash
# 1. Install Ollama: https://ollama.ai
# 2. Pull a model
ollama pull deepseek-r1

# 3. Install Python deps
pip install -r requirements.txt

# 4. Run
python main.py
```

### Demo Mode (no Ollama required)

```bash
set GIDBOY_DEMO=1  # Windows
export GIDBOY_DEMO=1  # Mac/Linux

python main.py
```

## Usage

```
> research solana L2 landscape
> /OPPORTUNITY find grants for researchers
> detect new DeFi trends
> /SIGNAL what's trending in crypto
> /EXECUTION draft outreach email
> /quit
```

## API

Start the FastAPI server:

```bash
pip install fastapi uvicorn
python api.py
```

Then POST to `/task`:

```bash
curl -X POST "http://localhost:8000/task" \
  -H "Content-Type: application/json" \
  -d '{"query": "research solana ecosystem"}'
```

## Modes

| Mode | Purpose | Example |
|------|---------|---------|
| RESEARCH | Crypto topic analysis | "research solana validator landscape" |
| OPPORTUNITY | Jobs/grants/fellowships | "find researcher grants" |
| SIGNAL | Early trend detection | "detect new DeFi narratives" |
| ANALYSIS | Data pattern analysis | "analyze solana fee trends" |
| CONTENT | Social media creation | "write thread about firedancer" |
| CAREER | Role matching | "career advice for researchers" |
| EXECUTION | Task completion | "draft email to investor" |

## Deployment

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

## Tech Stack

- Python 3.10+
- Ollama (local LLM inference)
- JSON-based memory (ChromaDB optional)
- FastAPI (API layer)

## License

MIT