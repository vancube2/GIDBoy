"""FastAPI backend for GIDBoy."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from router import route
from ollama_client import call_ollama
from prompts import SYSTEM_PROMPT, MODES
from memory import Memory

# Use demo mode if no Ollama available
if not os.environ.get("OLLAMA_URL"):
    os.environ["GIDBOY_DEMO"] = "1"

app = FastAPI(title="GIDBoy Intelligence OS", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize memory
memory = Memory(path="./data/memory_db.json")


class TaskRequest(BaseModel):
    query: str
    mode: Optional[str] = None
    use_memory: bool = True


class TaskResponse(BaseModel):
    mode: str
    query: str
    result: str
    memory_used: bool


@app.post("/task", response_model=TaskResponse)
def task(req: TaskRequest):
    """Execute a GIDBoy task."""
    # Route or use explicit mode
    if req.mode:
        mode = req.mode.upper()
        clean_query = req.query
    else:
        mode, clean_query = route(req.query)

    # Get memory context
    context = ""
    if req.use_memory:
        memories = memory.search(clean_query, n=2)
        if memories:
            context = f"\nRELEVANT MEMORY:\n{memories}\n"

    # Build prompt
    prompt = f"""{SYSTEM_PROMPT}

MODE: {mode}

{context}

TASK:
{clean_query}

INSTRUCTIONS:
{MODES.get(mode, "Respond concisely.")}
"""

    # Call Ollama
    result = call_ollama(prompt)

    # Store to memory
    memory.store(clean_query, result, mode)

    return TaskResponse(
        mode=mode,
        query=clean_query,
        result=result,
        memory_used=bool(context)
    )


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "modes": list(MODES.keys())}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "GIDBoy Intelligence OS",
        "version": "1.0.0",
        "modes": list(MODES.keys()),
        "endpoints": ["/task", "/health"]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)