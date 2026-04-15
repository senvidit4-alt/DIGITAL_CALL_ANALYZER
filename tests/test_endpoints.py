"""
tests/test_endpoints.py
=======================
Basic endpoint tests for MCA Cyber Dost backend.
Run with:  pytest tests/
"""

import sys
import os

# Ensure project root is importable when running from any directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# SYSTEM ENDPOINTS
# ---------------------------------------------------------------------------

def test_ping(client):
    res = client.get("/ping")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_health(client):
    res  = client.get("/health")
    data = res.get_json()
    assert res.status_code == 200
    assert "db_connected" in data
    assert "model_loaded" in data
    assert "uptime"       in data


def test_stats(client):
    res  = client.get("/stats")
    data = res.get_json()
    assert res.status_code == 200
    assert "total_analyzed" in data
    assert "scams_flagged"  in data
    assert "uptime"         in data


def test_history(client):
    res  = client.get("/history")
    data = res.get_json()
    assert res.status_code == 200
    assert "results" in data
    assert "count"   in data
    assert isinstance(data["results"], list)


def test_history_limit(client):
    res  = client.get("/history?limit=5")
    data = res.get_json()
    assert res.status_code == 200
    assert data["count"] <= 5


# ---------------------------------------------------------------------------
# /analyze — TEXT
# ---------------------------------------------------------------------------

def test_analyze_scam_text(client):
    payload = {"text": "Main CBI officer hoon, aapko arrest karenge, OTP batao turant."}
    res  = client.post("/analyze", json=payload)
    data = res.get_json()
    assert res.status_code == 200
    assert data["verdict"] in ("SCAM", "WARNING")
    assert data["score"]   >  0
    assert "escape_script"     in data
    assert "detected_signals"  in data
    assert "stage_tracker"     in data


def test_analyze_safe_text(client):
    payload = {"text": "Aaj mausam bahut accha hai, main park me gaya tha."}
    res  = client.post("/analyze", json=payload)
    data = res.get_json()
    assert res.status_code == 200
    assert data["verdict"] == "SAFE"


def test_analyze_missing_body(client):
    res = client.post("/analyze", json={})
    assert res.status_code == 400


def test_analyze_empty_text(client):
    res = client.post("/analyze", json={"text": "   "})
    assert res.status_code == 400


def test_analyze_text_too_long(client):
    res = client.post("/analyze", json={"text": "a" * 6000})
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# /feedback
# ---------------------------------------------------------------------------

def test_feedback_missing_fields(client):
    res = client.post("/feedback", json={"analysis_id": 1})
    assert res.status_code == 400


def test_feedback_invalid_id(client):
    res = client.post("/feedback", json={"analysis_id": "abc", "is_correct": True})
    assert res.status_code == 400


def test_feedback_invalid_is_correct(client):
    res = client.post("/feedback", json={"analysis_id": 1, "is_correct": "yes"})
    assert res.status_code == 400
