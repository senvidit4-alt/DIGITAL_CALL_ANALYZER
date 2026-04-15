"""
security/validators.py
======================
Input validation + lightweight in-memory rate limiter.
No external dependencies required.
"""

import time
from collections import defaultdict
from functools import wraps
from flask import request, jsonify

# ---------------------------------------------------------------------------
# RATE LIMITER
# ---------------------------------------------------------------------------
_rate_store: dict = defaultdict(list)
RATE_LIMIT  = 20   # max requests per window
RATE_WINDOW = 60   # seconds


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    # Drop timestamps outside the current window
    _rate_store[ip] = [t for t in _rate_store[ip] if now - t < RATE_WINDOW]
    if len(_rate_store[ip]) >= RATE_LIMIT:
        return True
    _rate_store[ip].append(now)
    return False


def rate_limit(f):
    """Decorator: returns 429 if the caller exceeds RATE_LIMIT req/min."""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr or "unknown"
        if _is_rate_limited(ip):
            return jsonify({
                "error":               "Too many requests. Please slow down.",
                "retry_after_seconds": RATE_WINDOW,
            }), 429
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# INPUT VALIDATORS
# ---------------------------------------------------------------------------
MAX_TEXT_LENGTH        = 5_000          # characters
ALLOWED_AUDIO_EXTS     = {"wav", "mp3", "ogg", "flac", "m4a"}
MAX_AUDIO_BYTES        = 10 * 1024 * 1024  # 10 MB


def validate_text(text: str):
    """Return an error string, or None if valid."""
    if not text or not text.strip():
        return "Text cannot be empty."
    if len(text) > MAX_TEXT_LENGTH:
        return f"Text too long. Maximum {MAX_TEXT_LENGTH} characters allowed."
    return None


def validate_audio_file(file) -> str | None:
    """Return an error string, or None if valid."""
    if file is None or file.filename == "":
        return "No audio file provided."

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_AUDIO_EXTS:
        return (
            f"Unsupported file type '.{ext}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_AUDIO_EXTS))}."
        )

    # Check size without loading whole file into RAM
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_AUDIO_BYTES:
        return "File too large. Maximum 10 MB allowed."

    return None
