# 🤝 MCA Cyber Dost — Team Handoff Guide

Backend is **live and ready**. Dono teammates ke liye integration guide neeche hai.

---

## 👤 P1 (Frontend / React) — Tumhara Integration Guide

### Base URL
```
http://localhost:5000
```

### CORS
Already enabled — koi setup nahi chahiye. Direct call karo.

---

### 📡 Endpoints — React se kaise call karein

#### 1. `POST /analyze` — Text analyze karo
```js
const res = await fetch("http://localhost:5000/analyze", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ text: "Main CBI officer hoon, OTP batao" })
});
const data = await res.json();
```

**Response:**
```json
{
  "score": 85.0,
  "verdict": "SCAM",
  "breakdown": {
    "ml_contribution": 40.0,
    "rule_contribution": 30.0,
    "multiplier_applied": true
  },
  "detected_signals": {
    "Authority": ["cbi", "officer"],
    "Extract": ["otp"]
  },
  "stage_tracker": {
    "current_stage": "Extract",
    "stages_hit": ["Authority", "Extract"]
  },
  "escape_script": "DO NOT share OTP..."
}
```

---

#### 2. `POST /analyze-audio` — Audio file analyze karo
```js
const formData = new FormData();
formData.append("audio", audioFile); // File object from input

const res = await fetch("http://localhost:5000/analyze-audio", {
  method: "POST",
  body: formData
});
const data = await res.json();
// Same as /analyze response + "transcript" field
```

---

#### 3. `GET /stats` — Dashboard counters
```js
const res = await fetch("http://localhost:5000/stats");
const data = await res.json();
// { total_analyzed: 47, scams_flagged: 31, uptime: "2h 15m", status: "online" }
```

---

#### 4. `GET /history` — Recent calls list
```js
const res = await fetch("http://localhost:5000/history?limit=10");
const data = await res.json();
// { results: [...], count: 10 }
```

**Each result:**
```json
{
  "id": 5,
  "input_text": "Main CBI officer hoon...",
  "score": 85.0,
  "verdict": "SCAM",
  "stage": "Extract",
  "source": "text",
  "timestamp": "2026-04-15 01:30:00"
}
```

---

#### 5. `GET /health` — Server status badge
```js
const res = await fetch("http://localhost:5000/health");
const data = await res.json();
// { status: "ok", db_connected: true, model_loaded: false, uptime: "1h 5m" }
```

---

#### 6. `POST /feedback` — "Was this result correct?" button
```js
const res = await fetch("http://localhost:5000/feedback", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    analysis_id: 5,       // from /history response
    is_correct: false,    // true or false
    comment: "This was a real call" // optional
  })
});
```

---

### Verdict Colors (React ke liye)
| Verdict | Color |
|---|---|
| `"SCAM"` | 🔴 Red |
| `"WARNING"` | 🟡 Yellow |
| `"SAFE"` | 🟢 Green |

---

---

## 👤 P2 (ML Model) — Tumhara Integration Guide

### Step 1 — Train your model

Tumhara model ek **text classifier** hona chahiye jo predict kare: **scam (1) ya not-scam (0)**.

**Input:** Raw text string (Hindi/Hinglish/English mix)  
**Output:** Probability — `[prob_safe, prob_scam]`

---

### Step 2 — Save model as `model.pkl`

```python
import joblib

# Train your pipeline (example with sklearn)
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression())
])
pipeline.fit(X_train, y_train)

# Save it
joblib.dump(pipeline, "model.pkl")
print("Saved!")
```

---

### Step 3 — Drop `model.pkl` in project root

```
mca-cyber-dost/
├── model.pkl   ← BAS YAHAN RAKH DO ✅
├── app.py
├── database.py
...
```

**Backend automatically load kar lega** — koi code change nahi.

---

### What Backend Expects from Your Model

```python
# Backend yeh call karta hai:
prob = model.predict_proba(["input text here"])[0][1]
# Returns: float between 0.0 and 1.0 (scam probability)
```

`scikit-learn` Pipeline use karo — seedha compatible hai.

---

### Database Schema (Analyzed data tumhe milega)

Agar training data chahiye past calls ka:
```sql
SELECT input_text, verdict FROM analyses;
-- verdict = 'SCAM' / 'WARNING' / 'SAFE'
-- Use SCAM=1, WARNING/SAFE=0 for binary classification
```

DB file: `mca-cyber-dost/cyber_dost.db` (SQLite)

```python
import sqlite3
conn = sqlite3.connect("cyber_dost.db")
df = pd.read_sql("SELECT input_text, verdict FROM analyses", conn)
```

---

### `/health` Endpoint Shows Model Status

```json
{
  "model_loaded": false,
  "model_note": "Using DummyClassifier until model.pkl is provided."
}
```

Jab `model.pkl` aa jayega:
```json
{
  "model_loaded": true,
  "model_note": "ML model active."
}
```

---

## 🔁 Integration Flow

```
P1 React UI
    │
    │  POST /analyze (text)
    │  POST /analyze-audio (file)
    │  GET  /stats, /history, /health
    ↓
P3 Flask Backend (tum)
    │
    │  process_text_analysis()
    │  transcribe_audio()
    │  save to SQLite DB
    ↓
P2 model.pkl
    │  predict_proba([text]) → scam probability
    │
    ↓
P2 Training Data ← GET from /history or cyber_dost.db
```
