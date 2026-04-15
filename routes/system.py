"""
routes/system.py
================
Blueprint for system/utility endpoints:
  GET  /ping      — Simple liveness check
  GET  /health    — Detailed health (DB + model status)
  GET  /stats     — Analysis counts (persistent, from DB)
  GET  /history   — Recent analysis results (?limit=N)
  POST /feedback  — Submit correctness rating for an analysis
"""

import time
from flask import Blueprint, request, jsonify

from database import get_stats, get_history, save_feedback
from services.analyzer import is_real_model_loaded

system_bp = Blueprint("system", __name__)

_START_TIME = time.time()


def _uptime_str() -> str:
    elapsed = int(time.time() - _START_TIME)
    h, rem  = divmod(elapsed, 3600)
    m, s    = divmod(rem, 60)
    return f"{h}h {m}m {s}s"


# ---------------------------------------------------------------------------
# GET /ping
# ---------------------------------------------------------------------------
@system_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "MCA Cyber Dost backend live!"}), 200


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------
@system_bp.route("/health", methods=["GET"])
def health():
    """Full health check — tells P2 whether DB and model are ready."""
    db_ok = True
    try:
        get_stats()
    except Exception:
        db_ok = False

    real_model = is_real_model_loaded()

    return jsonify({
        "status":       "ok" if db_ok else "degraded",
        "db_connected": db_ok,
        "model_loaded": real_model,
        "model_note": (
            "ML model active."
            if real_model
            else "Using rule engine + DummyClassifier — OK until P1 delivers model.pkl."
        ),
        "uptime": _uptime_str(),
    }), 200


# ---------------------------------------------------------------------------
# GET /stats
# ---------------------------------------------------------------------------
@system_bp.route("/stats", methods=["GET"])
def stats():
    """Persistent stats from DB — survives server restarts."""
    data = get_stats()
    data["uptime"] = _uptime_str()
    data["status"] = "online"
    return jsonify(data), 200


# ---------------------------------------------------------------------------
# GET /history
# ---------------------------------------------------------------------------
@system_bp.route("/history", methods=["GET"])
def history():
    """
    Returns last N analysis results.
    Query param: ?limit=20 (default 20, max 100)
    """
    try:
        limit = int(request.args.get("limit", 20))
        limit = max(1, min(limit, 100))
    except (ValueError, TypeError):
        limit = 20

    rows = get_history(limit=limit)
    return jsonify({"results": rows, "count": len(rows)}), 200


# ---------------------------------------------------------------------------
# POST /feedback
# ---------------------------------------------------------------------------
@system_bp.route("/feedback", methods=["POST"])
def feedback():
    """
    Accept user feedback on a specific analysis.
    Body: { "analysis_id": int, "is_correct": bool, "comment": str (optional) }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required."}), 400

    if "analysis_id" not in data:
        return jsonify({"error": "'analysis_id' is required."}), 400
    if "is_correct" not in data:
        return jsonify({"error": "'is_correct' (true/false) is required."}), 400

    try:
        analysis_id = int(data["analysis_id"])
    except (ValueError, TypeError):
        return jsonify({"error": "'analysis_id' must be an integer."}), 400

    if not isinstance(data["is_correct"], bool):
        return jsonify({"error": "'is_correct' must be a boolean (true or false)."}), 400

    fb_id = save_feedback(
        analysis_id=analysis_id,
        is_correct=data["is_correct"],
        comment=data.get("comment"),
    )

    return jsonify({
        "message":     "Feedback recorded. Thank you!",
        "feedback_id": fb_id,
    }), 201
