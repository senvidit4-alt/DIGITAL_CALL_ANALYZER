import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

START_TIME = time.time()

# --- HARDCODED RESPONSES ---

SCAM_RESPONSE = {
    "score": 100.0,
    "verdict": "SCAM",
    "breakdown": {
        "ml_contribution": 50.0,
        "rule_contribution": 50.0,
        "multiplier_applied": True
    },
    "detected_signals": {
        "Authority": ["cbi", "officer"],
        "Fear":      ["arrest", "warrant"],
        "Isolation": ["kisi ko mat batana"],
        "Urgency":   ["turant", "24 hours"],
        "Extract":   ["otp", "transfer"]
    },
    "stage_tracker": {
        "current_stage": "Extract",
        "stages_hit": ["Authority", "Fear", "Isolation", "Urgency", "Extract"]
    },
    "escape_script": "DO NOT share OTP or download any app. Say: 'I will visit my local bank branch physically.' Hang up and block the number."
}

WARNING_RESPONSE = {
    "score": 55.0,
    "verdict": "WARNING",
    "breakdown": {
        "ml_contribution": 30.0,
        "rule_contribution": 25.0,
        "multiplier_applied": False
    },
    "detected_signals": {
        "Authority": ["officer", "department"],
        "Fear":      ["case", "penalty"]
    },
    "stage_tracker": {
        "current_stage": "Fear",
        "stages_hit": ["Authority", "Fear"]
    },
    "escape_script": "Say: 'My network is dropping, I cannot hear you.' Hang up and verify by calling the official department number."
}

SAFE_RESPONSE = {
    "score": 8.0,
    "verdict": "SAFE",
    "breakdown": {
        "ml_contribution": 4.0,
        "rule_contribution": 4.0,
        "multiplier_applied": False
    },
    "detected_signals": {},
    "stage_tracker": {
        "current_stage": "Unknown",
        "stages_hit": []
    },
    "escape_script": None
}

# --- SCAM KEYWORDS FOR ROUTING ---
SCAM_WORDS   = ["cbi", "arrest", "otp", "transfer", "warrant", "police",
                 "court", "turant", "kisi ko mat batana", "upi", "account"]
WARNING_WORDS = ["officer", "department", "case", "penalty", "suspend", "block"]

def get_response(text):
    text_lower = text.lower()
    if any(w in text_lower for w in SCAM_WORDS):
        return SCAM_RESPONSE
    elif any(w in text_lower for w in WARNING_WORDS):
        return WARNING_RESPONSE
    return SAFE_RESPONSE

# --- ENDPOINTS ---

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok", "message": "MCA Cyber Dost backend live!"}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Please provide 'text' in JSON body"}), 400
    return jsonify(get_response(data['text'])), 200

@app.route('/analyze-audio', methods=['POST'])
def analyze_audio():
    # Fallback mein audio directly SCAM return karta hai demo ke liye
    response = dict(SCAM_RESPONSE)
    response["transcript"] = "Main CBI officer hoon, aapka arrest warrant hai, OTP batao turant."
    return jsonify(response), 200

@app.route('/stats', methods=['GET'])
def stats():
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return jsonify({
        "total_analyzed": 47,
        "scams_flagged":  31,
        "uptime":         f"{hours}h {minutes}m {seconds}s",
        "status":         "online"
    }), 200

if __name__ == '__main__':
    print("⚠️  FALLBACK MODE — Hardcoded demo responses!")
    print("📍 Endpoints: /ping  /analyze  /analyze-audio  /stats")
    app.run(host='0.0.0.0', port=5000, debug=True)