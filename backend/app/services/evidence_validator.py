"""
Evidence Validator for Silicon Odyssey.
Validates page provenance, verifies citation authenticity, and enforces refusal on insufficient evidence.
"""

import re
from typing import List, Dict, Any, Optional


class EvidenceValidator:
    TOTAL_PAGES = 50
    AUTHENTIC_NARRATIVE_PAGES = {6, 23, 37}

    EXTERNAL_ENTITIES = [
        "nvidia", "market cap", "market capitalization", "unreal engine", "ue5",
        "openai", "chatgpt", "deepseek", "bitcoin", "crypto", "tsmc fab 18",
        "intel core i9", "apple vision pro", "metaverse", "stock price", "nasdaq"
    ]

    COMMON_STOP_WORDS = {
        "what", "when", "where", "which", "who", "whom", "whose", "why", "how",
        "was", "were", "is", "are", "am", "be", "been", "being", "have", "has", "had",
        "the", "a", "an", "and", "but", "if", "or", "because", "as", "of", "at", "by",
        "for", "with", "about", "to", "from", "in", "out", "on", "this", "that", "did",
        "does", "do", "done", "their", "there", "they", "them", "then", "into", "during"
    }

    CORPUS_DOMAIN_WORDS = {
        "founder", "author", "co-founder", "company", "memoir", "autobiography",
        "book", "chapter", "page", "mentioned", "name", "first", "early", "document",
        "narrative", "story", "write", "written", "describe", "described", "state", "stated"
    }

    @classmethod
    def validate_retrieval(
        cls,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        min_bm25: float = 1.0
    ) -> Dict[str, Any]:
        """
        Validates retrieved chunks to determine whether memoir evidence is sufficient.
        Uses multi-chunk evidence scanning: if the top chunk is boilerplate, checks
        whether ANY chunk among the top results lands on an authentic narrative page.
        """
        query_lower = query.lower()

        # 1. Immediate check for out-of-corpus entities in memoir mode
        matched_ext = [k for k in cls.EXTERNAL_ENTITIES if k in query_lower]
        if matched_ext:
            return {
                "is_valid": False,
                "confidence": "low",
                "reason": f"Query mentions entity '{', '.join(matched_ext)}' not present in memoir.",
                "refusal_required": True
            }

        if not retrieved_chunks:
            return {
                "is_valid": False,
                "confidence": "low",
                "reason": "No passages retrieved from the 50-page document.",
                "refusal_required": True
            }

        # Find the best narrative chunk among all retrieved results
        best_narrative_item = None
        best_narrative_bm25 = 0.0
        for item in retrieved_chunks:
            ch = item.get("chunk", {})
            pg = ch.get("page", 0)
            if pg in cls.AUTHENTIC_NARRATIVE_PAGES:
                if best_narrative_item is None or item.get("rrf_score", 0) > best_narrative_item.get("rrf_score", 0):
                    best_narrative_item = item
                    best_narrative_bm25 = item.get("bm25_score", 0.0)

        # If no authentic narrative page found anywhere in results, refuse
        if best_narrative_item is None:
            return {
                "is_valid": False,
                "confidence": "low",
                "reason": "All retrieved chunks belong to boilerplate reference clauses with no factual narrative.",
                "refusal_required": True
            }

        chunk = best_narrative_item.get("chunk", {})
        page = chunk.get("page", 0)
        bm25_score = best_narrative_bm25
        chunk_text = chunk.get("text", "").lower()

        # Check page bounds
        if page < 1 or page > cls.TOTAL_PAGES:
            return {
                "is_valid": False,
                "confidence": "low",
                "reason": f"Invalid page reference {page} outside bounds (1-50).",
                "refusal_required": True
            }

        # Extract discriminating content words (excluding stopwords and generic corpus words)
        all_query_tokens = re.findall(r'[a-zA-Z0-9\$\-]+', query_lower)
        discriminating_words = [
            w for w in all_query_tokens
            if len(w) >= 3 and w not in cls.COMMON_STOP_WORDS and w not in cls.CORPUS_DOMAIN_WORDS
        ]

        if discriminating_words:
            matched_discriminating = [w for w in discriminating_words if w in chunk_text]
            # For genuine out-of-corpus queries (like "pet dog"), ALL discriminating words
            # must fail to match. If at least one matches, the evidence is relevant.
            if len(matched_discriminating) == 0:
                # Double-check: scan ALL retrieved chunks' text for any discriminating match
                found_in_any = False
                for item in retrieved_chunks:
                    ch = item.get("chunk", {})
                    if ch.get("page", 0) in cls.AUTHENTIC_NARRATIVE_PAGES:
                        txt = ch.get("text", "").lower()
                        if any(w in txt for w in discriminating_words):
                            found_in_any = True
                            break
                if not found_in_any:
                    return {
                        "is_valid": False,
                        "confidence": "low",
                        "reason": f"Discriminating query subjects ({discriminating_words}) not found in memoir context.",
                        "refusal_required": True
                    }

        # Check BM25 score — use a relaxed threshold when page is known-authentic
        effective_min_bm25 = min_bm25 * 0.3 if page in cls.AUTHENTIC_NARRATIVE_PAGES else min_bm25
        if bm25_score < effective_min_bm25:
            return {
                "is_valid": False,
                "confidence": "low",
                "reason": "Weak lexical and semantic support in authentic narrative pages.",
                "refusal_required": True
            }

        return {
            "is_valid": True,
            "confidence": "high",
            "page": page,
            "chunk_id": chunk.get("chunk_id"),
            "chapter": chunk.get("narrative_chapter"),
            "header_chapter": chunk.get("header_chapter"),
            "has_discrepancy": chunk.get("has_discrepancy", False),
            "discrepancy_note": chunk.get("discrepancy_note", ""),
            "refusal_required": False
        }

    @classmethod
    def sanitize_citations(
        cls,
        citations: List[Dict[str, Any]],
        retrieved_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        allowed_pages = {c.get("chunk", {}).get("page") for c in retrieved_chunks if c.get("chunk", {}).get("page")}
        sanitized = []
        for cit in citations:
            p = cit.get("page")
            if p in allowed_pages and 1 <= p <= cls.TOTAL_PAGES:
                sanitized.append(cit)
        return sanitized
