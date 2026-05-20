"""FastAPI backend for GIDBoy with LLM-based intelligent routing."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from llm_router import llm_route
from llm_client import call_llm_api
from prompts import SYSTEM_PROMPT, MODES
from memory import Memory

app = FastAPI(title="GIDBoy Intelligence OS", version="2.0.0")

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
    routing_confidence: Optional[float] = None


@app.post("/task", response_model=TaskResponse)
def task(req: TaskRequest):
    """Execute a GIDBoy task with LLM-based routing."""
    # Route or use explicit mode
    if req.mode:
        mode = req.mode.upper()
        clean_query = req.query
        confidence = 1.0
    else:
        mode, clean_query = llm_route(req.query)
        confidence = 0.9  # LLM routing confidence

    # Get memory context
    context = ""
    if req.use_memory:
        memories = memory.search(clean_query, n=2)
        if memories:
            context = f"\nRELEVANT MEMORY:\n{memories}\n"

    # Get mode-specific instructions
    mode_instructions = MODES.get(mode, "Respond concisely and accurately to the user's query.")

    # Build the full prompt
    prompt = f"""{SYSTEM_PROMPT}

MODE: {mode}

{context}

TASK:
{clean_query}

INSTRUCTIONS:
{mode_instructions}

Provide a comprehensive, accurate response tailored specifically to the task above."""

    # Call LLM API (Groq → Ollama → Demo fallback)
    result = call_llm_api(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2000
    )

    # Store to memory
    memory.store(clean_query, result, mode)

    return TaskResponse(
        mode=mode,
        query=clean_query,
        result=result,
        memory_used=bool(context),
        routing_confidence=confidence
    )


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "modes": list(MODES.keys()),
        "routing": "llm-based"
    }


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "GIDBoy Intelligence OS",
        "version": "2.0.0",
        "description": "LLM-based crypto research and opportunity intelligence",
        "modes": list(MODES.keys()),
        "endpoints": ["/task", "/health"],
        "routing": "llm-based"
    }


@app.get("/modes")
def get_modes():
    """Get available modes and their descriptions."""
    from llm_router import MODE_DEFINITIONS
    return {
        "modes": MODE_DEFINITIONS,
        "count": len(MODE_DEFINITIONS)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
