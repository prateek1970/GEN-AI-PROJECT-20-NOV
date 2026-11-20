"""
Query Router for Silicon Odyssey.
Routes user inquiries to Memoir Intelligence or Verified External Web Grounding.
"""

from typing import Dict, Any, List


class QueryRouter:
    EXTERNAL_KEYWORDS = [
        "nvidia", "market cap", "market capitalization", "unreal engine", "ue5",
        "openai", "chatgpt", "deepseek", "bitcoin", "crypto", "tsmc fab 18",
        "intel core i9", "apple vision pro", "metaverse", "stock price", "nasdaq"
    ]

    @classmethod
    def route(cls, query: str, forced_mode: str = "auto") -> Dict[str, Any]:
        """
        Routes the query.
        forced_mode: 'auto', 'memoir', or 'web'
        """
        if forced_mode in ["memoir", "web"]:
            return {
                "mode": forced_mode,
                "reason": f"Explicit mode override selected: {forced_mode}.",
                "is_out_of_corpus": forced_mode == "web"
            }

        q_lower = query.lower()
        matched_ext = [k for k in cls.EXTERNAL_KEYWORDS if k in q_lower]

        if matched_ext:
            return {
                "mode": "web",
                "reason": f"Query queries external modern entities: {', '.join(matched_ext)}.",
                "is_out_of_corpus": True,
                "matched_triggers": matched_ext
            }

        return {
            "mode": "memoir",
            "reason": "Query aligns with 1984-1991 microprocessor founder memoir.",
            "is_out_of_corpus": False,
            "matched_triggers": []
        }

