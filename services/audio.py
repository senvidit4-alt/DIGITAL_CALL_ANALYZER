"""
services/audio.py
=================
Audio transcription service.

Pipeline:
  1. Google Speech-to-Text (hi-IN)  — primary (free, fast)
  2. OpenAI Whisper (base model)    — fallback (offline, slower)
"""

import speech_recognition as sr

_whisper_model = None


def _get_whisper():
    """Lazy-load Whisper only when first needed (saves startup time)."""
    global _whisper_model
    if _whisper_model is None:
        print("⏳ Loading Whisper (base)…")
        import whisper
        _whisper_model = whisper.load_model("base")
        print("✅ Whisper ready.")
    return _whisper_model


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe a WAV/MP3/OGG file to text.
    Tries Google STT first; falls back to Whisper on failure.

    Args:
        file_path: Absolute path to the audio file.

    Returns:
        Transcribed text string.

    Raises:
        RuntimeError: If both methods fail.
    """
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)

    # --- Primary: Google STT ---
    try:
        print("☁️  Attempting Google STT…")
        text = recognizer.recognize_google(audio_data, language="hi-IN")
        print(f"✅ Google STT result: {text}")
        return text
    except Exception as google_err:
        print(f"⚠️  Google STT failed ({google_err}), falling back to Whisper…")

    # --- Fallback: Whisper ---
    try:
        model  = _get_whisper()
        result = model.transcribe(file_path, fp16=False)
        text   = result["text"]
        print(f"✅ Whisper result: {text}")
        return text
    except Exception as whisper_err:
        raise RuntimeError(
            f"Both Google STT and Whisper failed. "
            f"Google: {google_err}. Whisper: {whisper_err}."
        ) from whisper_err
