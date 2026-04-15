"""
routes/analysis.py
==================
Blueprint for analysis endpoints:
  POST /analyze        — Analyze text for scam patterns
  POST /analyze-audio  — Transcribe audio then analyze
"""

import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from services.analyzer import process_text_analysis
from services.audio     import transcribe_audio
from security.validators import rate_limit, validate_text, validate_audio_file
from database import save_analysis

analysis_bp = Blueprint("analysis", __name__)

# Temporary directory for uploaded audio files
_TEMP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp_uploads"
)
os.makedirs(_TEMP_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# POST /analyze
# ---------------------------------------------------------------------------
@analysis_bp.route("/analyze", methods=["POST"])
@rate_limit
def analyze_text():
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Please provide 'text' in JSON body."}), 400

    err = validate_text(data["text"])
    if err:
        return jsonify({"error": err}), 400

    result = process_text_analysis(data["text"])

    # Persist to DB (non-blocking — won't crash endpoint if DB fails)
    try:
        save_analysis(
            input_text=data["text"],
            score=result["score"],
            verdict=result["verdict"],
            stage=result["stage_tracker"]["current_stage"],
            source="text",
        )
    except Exception as db_err:
        print(f"⚠️  DB save failed (non-critical): {db_err}")

    return jsonify(result), 200


# ---------------------------------------------------------------------------
# POST /analyze-audio
# ---------------------------------------------------------------------------
@analysis_bp.route("/analyze-audio", methods=["POST"])
@rate_limit
def analyze_audio():
    file = request.files.get("audio")
    err  = validate_audio_file(file)
    if err:
        return jsonify({"error": err}), 400

    filename  = secure_filename(file.filename)
    temp_path = os.path.join(_TEMP_DIR, filename)
    file.save(temp_path)

    try:
        print("🎙️  Processing audio…")
        text   = transcribe_audio(temp_path)
        result = process_text_analysis(text)
        result["transcript"] = text
        result["message"]    = "Audio processed successfully!"

        try:
            save_analysis(
                input_text=text,
                transcript=text,
                score=result["score"],
                verdict=result["verdict"],
                stage=result["stage_tracker"]["current_stage"],
                source="audio",
            )
        except Exception as db_err:
            print(f"⚠️  DB save failed (non-critical): {db_err}")

        return jsonify(result), 200

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Audio processing failed: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
