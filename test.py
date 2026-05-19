import os
os.environ["GIDBOY_DEMO"] = "1"

from main import run_gidboy

test_queries = [
    "research solana ecosystem",
    "find grants for developers",
    "detect new DeFi trends",
]

print("=" * 60)
print("GIDBoy Test Run")
print("=" * 60)

for query in test_queries:
    print(f"\n\nQUERY: {query}")
    print("-" * 40)
    result = run_gidboy(query)
    print(f"[{result['mode']}]")
    print(result['result'][:800] + "...")

print("\n\n" + "=" * 60)
print("Demo complete. Run 'python main.py' for interactive mode.")
print("=" * 60)