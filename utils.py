# utils.py
import json, os
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt

DEFAULT_PALETTES = {
    "joy": ["#FFD166","#FF7B7B","#C4FCEF"],
    "sadness": ["#023E8A","#0077B6","#90E0EF"],
    "calm": ["#BDE0FE","#CAE9FF","#E8F8FF"],
    "anger": ["#EF476F","#FF7B2D","#F9C74F"],
    "hope": ["#FFB703","#8EC5FF","#FDE68A"],
    "neutral": ["#E2E8F0","#CBD5E1","#F8FAFC"]
}

def pick_palette_for_emotions(emotions: dict):
    # dominant emotion
    dom = max(emotions, key=emotions.get)
    # fallback
    palette_colors = DEFAULT_PALETTES.get(dom, DEFAULT_PALETTES['neutral'])
    background = "#0F172A" if dom in ["sadness","fear","anger"] else "#FFFFFF"
    return {"colors": palette_colors, "background": background}

def emotion_bar_chart(emotions: dict):
    labels = list(emotions.keys())
    vals = [emotions[k] for k in labels]
    fig, ax = plt.subplots(figsize=(4,1.2))
    ax.barh(labels, vals)
    ax.set_xlim(0,1)
    ax.axis('off')
    st.pyplot(fig)

def save_mood_entry(emotions: dict, text: str):
    entry = {"text": text, "emotions": emotions}
    p = "mood_history.json"
    if os.path.exists(p):
        data = json.load(open(p, "r"))
    else:
        data = []
    data.append(entry)
    json.dump(data, open(p, "w"), indent=2)
