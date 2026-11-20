#!/usr/bin/env python3
"""
CLI Evaluation Runner for Silicon Odyssey: Founder Intelligence Engine.
Executes the 5 official assessment questions + 1 unrelated abstention check.
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.app.config import DEFAULT_PDF_PATH, GEMINI_API_KEY
from backend.app.pdf_processor import PDFProcessor
from backend.app.retrieval.hybrid_search import HybridSearch
from backend.app.services.answer_service import AnswerService
from backend.app.eval_suite import AssessmentBenchmark


def main():
    parser = argparse.ArgumentParser(description="Silicon Odyssey Automated RAG Evaluation Benchmark Runner")
    parser.add_argument("--output", "-o", default="eval_results.json", help="Path to save evaluation JSON results")
    args = parser.parse_args()

    print("\n" + "=" * 76)
    print(" ⚡ SILICON ODYSSEY: AUTOMATED RAG EVALUATION BENCHMARK")
    print(" 'Every answer has a source. Every discovery has evidence.'")
    print("=" * 76)

    if not DEFAULT_PDF_PATH.exists():
        print(f"\n[!] ERROR: Memoir PDF not found at: {DEFAULT_PDF_PATH}")
        sys.exit(1)

    try:
        processor = PDFProcessor(str(DEFAULT_PDF_PATH))
        hybrid_search = HybridSearch(processor.get_all_chunks())
        answer_service = AnswerService(hybrid_search=hybrid_search, api_key=GEMINI_API_KEY)
        suite = AssessmentBenchmark(answer_service)
    except Exception as e:
        print(f"\n[!] ERROR initializing RAG benchmark engine: {e}")
        sys.exit(1)

    print("\n[+] Running Official Assessment Suite through Hybrid RAG Pipeline...\n")
    report = suite.run_all()
    summary = report.get("summary", {})
    results = report.get("results", [])

    for r in results:
        status_symbol = "✅ PASS" if r.get("pass") else "❌ FAIL"
        page_val = r.get("supporting_page")
        exp_val = r.get("expected_page")
        page_str = f"Page {page_val}" if page_val else "None (External / Abstain)"
        exp_str = f"Page {exp_val}" if exp_val else "None (External / Abstain)"
        mode_str = (r.get("mode") or "UNKNOWN").upper()
        conf_str = r.get("confidence") or "N/A"
        lat_ms = r.get("latency_ms", 0.0)
        preview = (r.get("answer_preview") or "").replace("\n", " ").strip()
        notes = r.get("notes") or ""

        print(f"----------------------------------------------------------------------------")
        print(f"[{r.get('id', 'TEST')}] {r.get('question', '')}")
        print(f"     Status: {status_symbol} | Mode: {mode_str} | Confidence: {conf_str}")
        print(f"     Page Retrieved: {page_str} (Expected: {exp_str}) | Latency: {lat_ms}ms")
        print(f"     Synthesis: {preview}")
        print(f"     Audit Note: {notes}")

    print("\n" + "=" * 76)
    print(" 🏆 BENCHMARK EXECUTIVE SUMMARY")
    print("=" * 76)
    print(f" Total Benchmark Tests:            {summary.get('total_questions', 0)}")
    print(f" Passed:                           {summary.get('passed', 0)}")
    print(f" Failed:                           {summary.get('failed', 0)}")
    print(f" Overall Accuracy:                 {summary.get('accuracy_percent', 0.0)}%")
    print(f" Refusal & Abstention Integrity:   {summary.get('refusal_integrity', 'N/A')}")
    print(f" Citation Precision:               {summary.get('citation_precision', 'N/A')}")
    print(f" External Grounding Accuracy:      {summary.get('external_grounding_accuracy', 'N/A')}")
    print(f" Final Exam Verdict:               {summary.get('verdict', 'N/A')}")
    print("=" * 76 + "\n")

    # Save to JSON output
    out_path = Path(args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[+] Detailed benchmark report saved to '{out_path}'.\n")

    # Non-zero exit code if failures detected
    if summary.get("failed", 0) > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
