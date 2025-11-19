#!/usr/bin/env python3
"""Quick sentiment API test."""

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Quick test: sentiment with special chars
resp = client.get('/api/sentiment?query=test%20query')
print(f'Sentiment endpoint status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'Response: keyword={data.get("keyword")}, total_results={data.get("total_results")}')
    print('[OK] Sentiment endpoint works')
elif resp.status_code >= 500:
    print(f'[ERROR] Server error: {resp.text[:300]}')
else:
    print(f'[WARN] Status {resp.status_code}: {resp.text[:200]}')
