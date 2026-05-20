"""GIDBoy CLI with LLM-based intelligent routing."""
from llm_router import llm_route
from llm_client import call_llm_api
from prompts import SYSTEM_PROMPT, MODES
from memory import Memory

memory = Memory()


def run_gidboy(query: str, use_memory: bool = True, verbose: bool = False) -> dict:
    """Run GIDBoy on a query with LLM-based routing."""

    # Route to mode using LLM
    mode, clean_query = llm_route(query)

    if verbose:
        print(f"[Routing: {mode}]")

    # Get memory context
    context = ""
    if use_memory:
        memories = memory.search(clean_query, n=2)
        if memories:
            context = f"\nRELEVANT MEMORY:\n{memories}\n"

    # Get mode instructions
    mode_instructions = MODES.get(mode, "Respond concisely and accurately to the user's query.")

    # Build prompt
    prompt = f"""{SYSTEM_PROMPT}

MODE: {mode}

{context}

TASK:
{clean_query}

INSTRUCTIONS:
{mode_instructions}

Provide a comprehensive, accurate response tailored specifically to the task above."""

    # Call LLM API (Groq → Ollama → Demo)
    response = call_llm_api(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=2000
    )

    # Store result
    memory.store(clean_query, response, mode)

    return {
        "mode": mode,
        "query": clean_query,
        "result": response
    }


def main():
    """CLI entry point."""
    print("╔════════════════════════════════════════════════╗")
    print("║     GIDBoy Intelligence OS v2.0                ║")
    print("║     LLM-Based Routing Enabled                ║")
    print("╚════════════════════════════════════════════════╝")
    print("\nCommands:")
    print("  /quit              - Exit the application")
    print("  /memory <query>    - Search memory")
    print("  /mode <m> <query>  - Force specific mode")
    print("  /modes             - List available modes")
    print("  /verbose           - Toggle verbose mode")
    print("\nModes: RESEARCH, OPPORTUNITY, SIGNAL, ANALYSIS, CONTENT, CAREER, EXECUTION")
    print("-" * 50)

    verbose = False

    while True:
        try:
            q = input("\n> ").strip()

            if not q:
                continue

            if q.lower() == "/quit":
                break

            if q.lower() == "/verbose":
                verbose = not verbose
                print(f"Verbose mode: {'ON' if verbose else 'OFF'}")
                continue

            if q.lower() == "/modes":
                print("\nAvailable modes:")
                for mode in ["RESEARCH", "OPPORTUNITY", "SIGNAL", "ANALYSIS", "CONTENT", "CAREER", "EXECUTION"]:
                    print(f"  • {mode}")
                print("\nUse /MODE <mode> <query> to force a specific mode")
                continue

            if q.lower().startswith("/memory"):
                query = q[8:].strip()
                results = memory.search(query, n=5)
                print(f"\nMemory results:")
                for r in results:
                    print(f"- {r[:200]}...")
                continue

            # Handle explicit mode
            if q.lower().startswith("/mode"):
                parts = q.split(maxsplit=2)
                if len(parts) >= 3:
                    forced_mode = parts[1].upper()
                    query = parts[2]
                    result = run_gidboy(f"/{forced_mode} {query}", use_memory=True, verbose=verbose)
                else:
                    print("Usage: /mode <MODE> <query>")
                    continue
            else:
                result = run_gidboy(q, use_memory=True, verbose=verbose)

            print(f"\n[{result['mode']}]")
            print("=" * 50)
            print(result['result'])

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

    print("\nGoodbye.")


if __name__ == "__main__":
    main()
