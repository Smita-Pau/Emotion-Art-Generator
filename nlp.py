# nlp.py
from transformers import pipeline
from textblob import TextBlob
import numpy as np
import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment

# Try to initialize a multi-emotion model
EMO_MODEL = None
try:
    # distilbert fine-tuned to emotion examples: use "arpanghoshal/EmoRoBERTa" or similar if available
    EMO_MODEL = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
except Exception as e:
    EMO_MODEL = None

EMO_LABELS = ["anger","disgust","fear","joy","neutral","sadness","surprise"]  # adjust per model

def _transcribe_audio_bytes(file_bytes, filetype):
    r = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=f".{filetype}", delete=False) as f:
        f.write(file_bytes.read())
        tmpname = f.name
    # convert to wav
    audio = AudioSegment.from_file(tmpname)
    wav_path = tmpname + ".wav"
    audio.export(wav_path, format="wav")
    with sr.AudioFile(wav_path) as source:
        audio_data = r.record(source)
    try:
        return r.recognize_google(audio_data)
    except Exception:
        return ""

def detect_emotions(text="", audio_file=None):
    """Return dict of emotion scores normalized to 0-1"""
    combined_text = text or ""
    if audio_file is not None:
        try:
            trans = _transcribe_audio_bytes(audio_file, audio_file.type.split("/")[-1])
            combined_text += " " + trans
        except Exception:
            pass

    if EMO_MODEL:
        try:
            outs = EMO_MODEL(combined_text[:1000])  # returns list
            scores = {d['label'].lower(): d['score'] for d in outs[0]}
            # normalize to our labels
            # ensure all labels present
            for lab in EMO_LABELS:
                scores.setdefault(lab, 0.0)
            # map hope heuristically: if 'joy' + 'neutral' high and words suggest hope
            if 'joy' in scores and 'neutral' in scores:
                scores['hope'] = max(0.0, (scores['joy'] - scores['neutral']) * 0.8)
            # include hope in final dict
            final = {k: float(scores.get(k, 0.0)) for k in ["joy","sadness","anger","fear","surprise","disgust","neutral"]}
            final['hope'] = float(scores.get('hope', 0.0))
            # normalize
            s = sum(final.values()) or 1.0
            final = {k: v/s for k,v in final.items()}
            return final
        except Exception:
            pass

    # Fallback: TextBlob polarity → coarse mapping
    tb = TextBlob(combined_text)
    p = tb.sentiment.polarity  # -1..1
    final = {
        "joy": max(0, p),
        "sadness": max(0, -p),
        "anger": 0.0,
        "fear": 0.0,
        "surprise": 0.0,
        "disgust": 0.0,
        "neutral": 1 - abs(p),
        "hope": max(0, p*0.5)
    }
    s = sum(final.values()) or 1.0
    final = {k: v/s for k,v in final.items()}
    return final
