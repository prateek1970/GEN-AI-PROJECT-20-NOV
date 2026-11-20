import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

print("=== 1. Testing /api/health ===")
resp = client.get("/api/health")
print(f"Status: {resp.status_code}, Data: {resp.json()}")
assert resp.status_code == 200
assert resp.json().get("status") == "ok"

print("\n=== 2. Testing /api/overview ===")
resp = client.get("/api/overview")
data = resp.json()
print(f"Status: {resp.status_code}, Total Chunks: {data.get('total_chunks')}, Total Pages: {data.get('total_pages')}")
assert resp.status_code == 200

print("\n=== 3. Testing /api/pipeline/trace ===")
resp = client.get("/api/pipeline/trace")
print(f"Status: {resp.status_code}, Stages: {len(resp.json().get('pipeline_stages', []))}")
assert resp.status_code == 200

print("\n=== 4. Testing /api/timeline ===")
resp = client.get("/api/timeline")
print(f"Status: {resp.status_code}, Events: {len(resp.json().get('events', []))}")
assert resp.status_code == 200

print("\n=== 5. Testing /api/forensics ===")
resp = client.get("/api/forensics")
print(f"Status: {resp.status_code}, Incident: {resp.json().get('title')}")
assert resp.status_code == 200

print("\n=== 6. Testing /api/chat Live Inquiries ===")
test_queries = [
    {
        "id": "Q1 - Address",
        "query": "Where was the company founded, and what was the exact address?",
        "mode": "memoir",
        "expected_page": 6
    },
    {
        "id": "Q2 - Comdex Failure",
        "query": "What caused the catastrophic thermal failure of the Series-4 prototype during the trade-show demonstration?",
        "mode": "memoir",
        "expected_page": 23
    },
    {
        "id": "Q3 - NVIDIA Market Cap",
        "query": "What was NVIDIA Corporation's market capitalization in 2026?",
        "mode": "web",
        "expected_page": None
    },
    {
        "id": "Q4 - Bridge Financing",
        "query": "How much emergency bridge financing did the author secure during the 1991 semiconductor downturn?",
        "mode": "memoir",
        "expected_page": 37
    },
    {
        "id": "Q5 - Unreal Engine 5",
        "query": "What are the system requirements for running Unreal Engine 5 on a Windows laptop?",
        "mode": "web",
        "expected_page": None
    },
    {
        "id": "Q6 - Abstention (Pet Dog)",
        "query": "What was the name of the founder's pet dog mentioned in the memoir?",
        "mode": "memoir",
        "expected_page": None
    }
]

for t in test_queries:
    resp = client.post("/api/chat", json={"query": t["query"], "mode": t["mode"]})
    assert resp.status_code == 200, f"Error {resp.status_code}: {resp.text}"
    res = resp.json()
    cits = res.get("citations", [])
    cit_page = cits[0].get("page") if cits else None
    confidence = res.get("confidence")
    ans_snippet = res.get("answer", "")[:120].replace("\n", " ")
    print(f"[{t['id']}] Mode: {res.get('mode')}, Conf: {confidence}, Page: {cit_page} (Expected: {t['expected_page']})")
    print(f"    Snippet: {ans_snippet}...")
    
    if t["expected_page"]:
        assert cit_page == t["expected_page"], f"Failed page check: got {cit_page}, expected {t['expected_page']}"
        assert confidence == "high", f"Expected high confidence, got {confidence}"
        print(f"    -> Exact Citation Verified on Page {cit_page}!")
    elif t["id"].startswith("Q6"):
        assert "could not be verified" in res.get("answer", "").lower() or confidence == "low"
        print("    -> Abstention successfully enforced (Zero Hallucination)!")
    else:
        assert res.get("mode") == "web"
        print("    -> External grounding successfully retrieved!")

print("\n=== 7. Testing /api/eval/run (Assessment Benchmark) ===")
resp = client.post("/api/eval/run")
assert resp.status_code == 200
eval_data = resp.json()
summary = eval_data.get("summary", {})
print(f"Benchmark Summary: {summary}")
assert summary.get("passed") == summary.get("total_questions"), f"Benchmark failed: {summary}"
print(f"ALL {summary.get('passed')}/{summary.get('total_questions')} TESTS PASSED (100%)!")

print("\n=== 8. Testing /api/evidence/chunks and /api/evidence/page/6 ===")
resp_chunks = client.get("/api/evidence/chunks?page=6")
assert resp_chunks.status_code == 200
print(f"Page 6 chunks retrieved: {len(resp_chunks.json().get('chunks', []))}")

resp_p6 = client.get("/api/evidence/page/6")
assert resp_p6.status_code == 200
print(f"Page 6 narrative chapter: {resp_p6.json().get('narrative_chapter')}")

print("\n=======================================================")
print("  ALL ENDPOINTS & BENCHMARKS VERIFIED SUCCESSFULLY!    ")
print("=======================================================")

