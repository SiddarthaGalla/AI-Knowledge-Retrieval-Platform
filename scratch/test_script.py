import urllib.request
import json

def test_query(q):
    url = "http://127.0.0.1:8000/api/query"
    payload = {"query": q, "domain_filter": "all"}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        p = data["data"]
        print(f"\n==========================================")
        print(f"QUERY: {q}")
        print(f"CONFIDENCE: {p['confidence_score']:.2f} ({p['confidence_level']})")
        print(f"DOMAIN: {p.get('domain')}")
        print(f"CITATIONS COUNT: {len(p.get('citations', []))}")
        safe_resp = p['response_text'].encode('ascii', 'replace').decode()
        print(f"RESPONSE:\n{safe_resp}")
        print(f"==========================================")

if __name__ == "__main__":
    # Test 1: Query that does NOT exist in any uploaded document
    test_query("What is the recipe for baking chocolate chip cookies?")
    
    # Test 2: In-document query
    test_query("What is the waiting period for medical coverage?")
