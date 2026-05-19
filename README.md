# GIDBoy

**Autonomous crypto research and opportunity intelligence agent.**

A complete product with CLI, API, and web interface. GIDBoy helps researchers, developers, and analysts find opportunities, detect signals, and execute tasks in the crypto space.

🌐 **Live Demo**: [vancube2.github.io/GIDBoy](https://vancube2.github.io/GIDBoy)

## Features

- **7 Intelligence Modes**: Research, Opportunity, Signal, Analysis, Content, Career, Execution
- **Smart Routing**: Automatic mode detection based on query intent
- **Persistent Memory**: Remembers past research and patterns
- **Dual Targeting**: Opportunities for both crypto-native and traditional researchers
- **Web UI**: Modern chat interface with mode selector and history
- **CLI**: Terminal-based interface for power users
- **API**: RESTful endpoints for integration

## Try It Now

### Web Interface (Recommended)

Visit the live demo: **https://vancube2.github.io/GIDBoy**

Or run locally:

```bash
npm install
npm run dev
# Open http://localhost:3000
```

### CLI (Terminal)

```bash
# Install dependencies
pip install -r requirements.txt

# Run in demo mode (no Ollama required)
python main.py

# Or with Ollama
ollama pull deepseek-r1
python main.py
```

## Usage Examples

| Mode | Example Query | Output |
|------|-------------|--------|
| **RESEARCH** | "research solana L2 landscape" | Structured analysis with insights, opportunities, actions |
| **OPPORTUNITY** | "find grants for researchers" | Jobs, grants, fellowships (crypto + non-crypto) |
| **SIGNAL** | "detect new DeFi trends" | Early signals and emerging narratives |
| **ANALYSIS** | "analyze solana fee trends" | Data-driven pattern analysis |
| **CONTENT** | "write thread about firedancer" | X threads, LinkedIn posts |
| **CAREER** | "career advice for researchers" | Role matching and positioning |
| **EXECUTION** | "draft outreach email" | Task breakdown and templates |

## Project Structure

```
gidboy/
├── src/                    # Next.js frontend source
│   └── app/
│       ├── page.tsx       # Main chat interface
│       ├── layout.tsx     # Root layout
│       └── globals.css    # Dark theme styles
├── main.py                # CLI entry point
├── api.py                 # FastAPI server
├── router.py              # Mode detection logic
├── ollama_client.py       # LLM integration
├── memory.py              # Persistent storage
├── modes/                 # Mode prompt templates
│   ├── research.txt
│   ├── opportunity.txt
│   ├── signal.txt
│   ├── analysis.txt
│   ├── content.txt
│   ├── career.txt
│   └── execution.txt
└── .github/workflows/     # Auto-deployment
    ├── deploy-ui.yml      # GitHub Pages
    └── railway-deploy.yml # Railway backend
```

## Deployment

### Frontend (GitHub Pages)

The web UI auto-deploys to GitHub Pages on every push to `main`.

**Live URL**: `https://vancube2.github.io/GIDBoy`

### Backend (Railway)

Deploy the API to Railway:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/vancube2/GIDBoy)

Or manually:

```bash
railway login
railway init
railway up
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| AI | Ollama (local), Demo mode (fallback) |
| Memory | JSON-based persistence |
| Deployment | GitHub Pages (UI), Railway (API) |

## License

MIT