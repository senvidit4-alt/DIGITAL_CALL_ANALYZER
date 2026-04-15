"""
app.py — MCA Cyber Dost Backend Entry Point
============================================

All endpoints:
  GET  /ping           — Liveness check
  GET  /health         — DB + model status
  GET  /stats          — Persistent analysis counts
  GET  /history        — Recent analysis results (?limit=N)
  POST /analyze        — Analyze text for scam patterns
  POST /analyze-audio  — Analyze audio file (transcribe + analyze)
  POST /feedback       — Submit correctness rating

Run:  python app.py
Test: pytest tests/
"""

from flask import Flask
from flask_cors import CORS

from database import init_db
from routes.analysis import analysis_bp
from routes.system   import system_bp


def create_app() -> Flask:
    """Application factory — used by both the server and the test suite."""
    app = Flask(__name__)

    # Ensure non-ASCII (Hindi/Hinglish) characters are not escaped in JSON
    app.json.ensure_ascii = False
    app.config["JSON_AS_ASCII"] = False

    # CORS — allow React dev server (P2) and any localhost port
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Set up SQLite tables on first run
    init_db()

    # Register route blueprints
    app.register_blueprint(analysis_bp)
    app.register_blueprint(system_bp)

    return app


# ---------------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    print("🚀 MCA Cyber Dost Backend starting…")
    print("📍 Endpoints:")
    print("     GET  /ping  /health  /stats  /history")
    print("     POST /analyze  /analyze-audio  /feedback")
    app.run(host="0.0.0.0", port=5000, debug=True)