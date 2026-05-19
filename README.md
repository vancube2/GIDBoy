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

### Railway (Auto-Deploy on Push)

**One-Click Deploy:**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/vancube2/GIDBoy)

**Manual Setup:**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and create project
railway login
railway init

# 3. Get token for GitHub Actions
railway token

# 4. Add token to GitHub Secrets (Settings -> Secrets -> RAILWAY_TOKEN)
```

**GitHub Actions Auto-Deploy:**

The repo includes `.github/workflows/railway-deploy.yml` that automatically deploys on every push to `main`.

Setup required:
1. Go to Railway Dashboard → Project Settings → Generate Token
2. Copy the token
3. Go to GitHub Repo → Settings → Secrets → New repository secret
4. Name: `RAILWAY_TOKEN`
5. Value: Paste the token
6. Save and push any change to trigger deploy

## Tech Stack

- Python 3.10+
- Ollama (local LLM inference)
- JSON-based memory (ChromaDB optional)
- FastAPI (API layer)

## License

MIT