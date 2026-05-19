from router import route
from ollama_client import call_ollama
from prompts import SYSTEM_PROMPT, MODES
from memory import Memory

memory = Memory()

def run_gidboy(query: str, use_memory: bool = True) -> dict:
    """Run GIDBoy on a query."""

    # Route to mode
    mode, clean_query = route(query)

    # Get memory context
    context = ""
    if use_memory:
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
    response = call_ollama(prompt)

    # Store result
    memory.store(clean_query, response, mode)

    return {
        "mode": mode,
        "query": clean_query,
        "result": response
    }

def main():
    """CLI entry point."""
    print("GIDBoy Intelligence OS")
    print("Commands: /quit, /memory <query>, /mode <mode> <query>")
    print("-" * 50)

    while True:
        try:
            q = input("\n> ").strip()

            if not q:
                continue

            if q.lower() == "/quit":
                break

            if q.lower().startswith("/memory"):
                query = q[8:].strip()
                results = memory.search(query, n=5)
                print(f"\nMemory results:")
                for r in results:
                    print(f"- {r[:200]}...")
                continue

            result = run_gidboy(q)

            print(f"\n[{result['mode']}]")
            print(result['result'])

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

    print("\nGoodbye.")

if __name__ == "__main__":
    main()