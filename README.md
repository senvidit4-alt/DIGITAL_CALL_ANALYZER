<<<<<<< HEAD
# Digital-call-analyzer
=======
# MCA Cyber Dost - AI Scam Call Detector 🇮🇳

MCA Cyber Dost is a Flask-powered backend designed to detect scam calls in real-time. It uses a combination of Rule-based engines and ML models to analyze text and audio for suspicious patterns common in Indian cyber scams.

## 🚀 Features

- **Multi-lingual Support**: Recognizes English, Hinglish, and Devanagari (Hindi) keywords.
- **Dual STT Engine**: Uses Google Speech-to-Text with a local **Whisper** fallback for reliable audio transcription.
- **Rule-based & ML Analysis**: A hybrid scoring system that categorizes calls into **SCAM**, **WARNING**, or **SAFE**.
- **Stage Tracking**: Monitors the progression of a scam across 5 stages: Authority, Fear, Isolation, Urgency, and Extract.
- **Escape Scripts**: Provides immediate actionable advice for users based on the detected scam stage.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Audio Processing**: SpeechRecognition, OpenAI Whisper
- **ML**: Joblib (Pipeline integration)
- **CORS**: Enabled for frontend integration (Port 5173)

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/senvidit4-alt/Digital-call-analyzer.git
   cd Digital-call-analyzer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   python app.py
   ```

## 📍 API Endpoints

- `GET /ping`: Health check.
- `POST /analyze`: Analyze raw text JSON: `{"text": "..."}`.
- `POST /analyze-audio`: Upload a `.wav` file to analyze audio.
- `GET /stats`: View system stats (total analyzed, scams flagged, uptime).

## 🛡️ Privacy & Security

- Audio files are processed locally or via Google STT and deleted immediately after analysis.
- No sensitive user data is stored persistently.

---
*Built for the safety of Indian citizens against cyber fraud.*
>>>>>>> 26d239b (Initial commit for MCA Cyber Dost Backend)
