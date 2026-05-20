"""GIDBoy Memory Agent - Long-term intelligence persistence."""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentState
import hashlib
import json


class MemoryAgent(BaseAgent):
    """
    Memory Agent manages long-term intelligence:
    - Store research findings
    - Retrieve relevant context
    - Connect recurring themes
    - Detect emerging patterns
    """

    def __init__(self, llm_client=None, vector_store=None):
        super().__init__("Memory", llm_client)
        self.vector_store = vector_store  # ChromaDB or similar
        self.session_memory = []

    def process(self, state: AgentState) -> AgentState:
        """Execute memory operations."""
        self.log_reasoning("start", "Processing memory operations")

        # Retrieve relevant memories
        relevant_memories = self._retrieve_memories(state.query)

        # Enrich state with memory context
        state.memory = relevant_memories

        # Store current research if completed
        if state.status == "completed":
            self._store_research(state)

        self.log_reasoning("complete", f"Retrieved {len(relevant_memories)} relevant memories")

        return state

    def _retrieve_memories(self, query: str, n: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on query."""
        if self.vector_store:
            # Use vector search if available
            try:
                results = self.vector_store.similarity_search(query, k=n)
                return [
                    {
                        "query": r.get("query", ""),
                        "response": r.get("response", ""),
                        "mode": r.get("mode", "unknown"),
                        "timestamp": r.get("timestamp", ""),
                        "relevance": r.get("score", 0)
                    }
                    for r in results
                ]
            except Exception as e:
                print(f"Vector search failed: {e}, using keyword fallback")

        # Fallback to keyword matching
        return self._keyword_search(query, n)

    def _keyword_search(self, query: str, n: int) -> List[Dict[str, Any]]:
        """Simple keyword-based memory search."""
        query_words = set(query.lower().split())
        scored_memories = []

        for mem in self.session_memory:
            mem_text = f"{mem.get('query', '')} {mem.get('response', '')}".lower()
            mem_words = set(mem_text.split())
            score = len(query_words & mem_words)

            if score > 0:
                scored_memories.append((score, mem))

        scored_memories.sort(reverse=True, key=lambda x: x[0])
        return [mem for _, mem in scored_memories[:n]]

    def _store_research(self, state: AgentState) -> None:
        """Store research findings to memory."""
        memory_entry = {
            "id": self._generate_id(state.query),
            "query": state.query,
            "mode": state.mode,
            "output": state.output,
            "timestamp": self._get_timestamp(),
            "reasoning": state.reasoning
        }

        # Store in session memory
        self.session_memory.append(memory_entry)

        # Store in vector database if available
        if self.vector_store:
            try:
                self._store_in_vector_db(memory_entry)
            except Exception as e:
                print(f"Vector DB storage failed: {e}")

    def _store_in_vector_db(self, entry: Dict[str, Any]) -> None:
        """Store entry in vector database."""
        # Prepare text for embedding
        text = f"Query: {entry['query']}\n\n"

        # Add key research findings
        research = entry.get("output", {}).get("research", {})
        text += f"Summary: {research.get('executive_summary', '')}\n"
        text += f"Findings: {', '.join(str(f) for f in research.get('key_findings', [])[:3])}\n"

        # Add opportunities
        opportunities = entry.get("output", {}).get("opportunities", [])
        if opportunities:
            text += f"Opportunities: {', '.join(str(o.get('name', '')) for o in opportunities[:3])}\n"

        # Store with metadata
        metadata = {
            "query": entry["query"],
            "mode": entry["mode"],
            "timestamp": entry["timestamp"],
            "id": entry["id"]
        }

        try:
            self.vector_store.add_texts([text], [metadata])
        except Exception as e:
            print(f"Failed to store in vector DB: {e}")

    def _generate_id(self, query: str) -> str:
        """Generate unique ID for memory entry."""
        hash_input = f"{query}_{self._get_timestamp()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_related_memories(self, theme: str, n: int = 5) -> List[Dict[str, Any]]:
        """Get memories related to a specific theme."""
        return self._retrieve_memories(theme, n)

    def detect_patterns(self) -> List[Dict[str, Any]]:
        """Detect patterns across memories."""
        if len(self.session_memory) < 2:
            return []

        # Simple pattern detection - find recurring keywords
        from collections import Counter

        all_words = []
        for mem in self.session_memory:
            query_words = mem.get("query", "").lower().split()
            all_words.extend([w for w in query_words if len(w) > 3])

        word_counts = Counter(all_words)
        recurring = [(word, count) for word, count in word_counts.items() if count > 1]
        recurring.sort(key=lambda x: x[1], reverse=True)

        return [
            {
                "theme": word,
                "frequency": count,
                "type": "recurring_keyword"
            }
            for word, count in recurring[:10]
        ]
