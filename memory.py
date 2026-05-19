import json
import os
from datetime import datetime
from typing import List, Dict

class Memory:
    def __init__(self, path: str = "./memory_db.json"):
        self.path = path
        self.memories = []
        self._load()

    def _load(self):
        """Load memories from disk."""
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    self.memories = json.load(f)
            except:
                self.memories = []

    def _save(self):
        """Save memories to disk."""
        with open(self.path, 'w') as f:
            json.dump(self.memories, f, indent=2)

    def store(self, query: str, response: str, mode: str):
        """Store task result."""
        entry = {
            "id": f"{mode}_{hash(query)}_{int(datetime.now().timestamp())}",
            "mode": mode,
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "query_hash": str(hash(query))
        }
        self.memories.append(entry)
        self._save()

    def search(self, query: str, n: int = 3, mode: str = None) -> List[str]:
        """Search relevant memories by keyword matching."""
        query_words = set(query.lower().split())
        scored = []

        for mem in self.memories:
            if mode and mem.get("mode") != mode:
                continue

            mem_text = f"{mem['query']} {mem['response']}".lower()
            mem_words = set(mem_text.split())
            score = len(query_words & mem_words)

            if score > 0:
                scored.append((score, mem))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [f"MODE: {m['mode']}\nQUERY: {m['query']}\nRESPONSE: {m['response'][:500]}"
                for _, m in scored[:n]]