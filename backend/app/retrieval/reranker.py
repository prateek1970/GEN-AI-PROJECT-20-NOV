"""
Reranker and Evidence Deduplication Engine.
Removes redundant overlapping chunks and scores evidence chunks for synthesis.
"""

from typing import List, Dict, Any


class EvidenceReranker:
    def __init__(self, redundancy_threshold: float = 0.75):
        self.redundancy_threshold = redundancy_threshold

    def _jaccard_similarity(self, text_a: str, text_b: str) -> float:
        set_a = set(text_a.lower().split())
        set_b = set(text_b.lower().split())
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)

    def rerank_and_deduplicate(
        self,
        retrieved_items: List[Dict[str, Any]],
        max_evidence: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Deduplicates overlapping chunks from the same page, selects top evidence chunks,
        and formats clean evidence items.
        """
        if not retrieved_items:
            return []

        selected: List[Dict[str, Any]] = []

        for item in retrieved_items:
            chunk = item.get("chunk", {})
            text = chunk.get("text", "")
            page = chunk.get("page", 0)

            # Check redundancy against already selected items
            is_redundant = False
            for s in selected:
                s_chunk = s.get("chunk", {})
                if s_chunk.get("page") == page:
                    sim = self._jaccard_similarity(text, s_chunk.get("text", ""))
                    if sim > self.redundancy_threshold:
                        is_redundant = True
                        break

            if not is_redundant:
                selected.append(item)
                if len(selected) >= max_evidence:
                    break

        return selected

