# app.py
import streamlit as st
from nlp import detect_emotions
from artgen import generate_art_image
from utils import save_mood_entry, emotion_bar_chart, DEFAULT_PALETTES
from io import BytesIO
from PIL import Image
import base64
import json
import os

st.set_page_config(page_title="Emotion → Art", layout="wide")

st.title("Emotion-to-Art Generator")
st.write("Type or speak how you feel — watch your emotion turn into art.")

# Input
col1, col2 = st.columns([2,1])
with col1:
    text_input = st.text_area("Describe your feeling (e.g., 'I feel hopeful and calm')", height=100)
    uploaded_audio = st.file_uploader("Or upload a short audio (wav/mp3)", type=["wav","mp3"])
    if st.button("Generate Art"):
        user_text = text_input.strip()
        with st.spinner("Analyzing..."):
            emotions = detect_emotions(user_text, uploaded_audio)
        st.session_state['last_emotions'] = emotions

with col2:
    st.subheader("Controls")
    style = st.selectbox("Style", ["Hybrid (Mandala+Abstract)", "Mandala", "Abstract", "Watercolor"])
    complexity = st.slider("Complexity", 1, 10, 5)
    color_intensity = st.slider("Color Intensity", 1, 10, 6)
    regenerate = st.button("Regenerate")

# If no emotions yet, show sample
if 'last_emotions' not in st.session_state:
    st.info("Enter text or audio and click Generate Art.")
    st.write("Sample palettes:")
    for k,v in DEFAULT_PALETTES.items():
        st.write(f"**{k}**: {', '.join(v)}")
    st.stop()

emotions = st.session_state['last_emotions']
st.subheader("Mood Meter")
emotion_bar_chart(emotions)

dominant = max(emotions, key=emotions.get)
st.markdown(f"**Dominant emotion:** {dominant.capitalize()}")

# Generate art image
img = generate_art_image(emotions,
                         style=style,
                         complexity=complexity,
                         color_intensity=color_intensity,
                         seed=None)

# Display
colA, colB = st.columns([3,1])
with colA:
    st.image(img, use_column_width=True)
    buf = BytesIO()
    img.save(buf, format='PNG')
    st.download_button("Download PNG", data=buf.getvalue(), file_name="emotion_art.png", mime="image/png")

with colB:
    if st.button("Save to Mood Diary"):
        save_mood_entry(emotions, text_input)
        st.success("Saved to mood_history.json")

st.write("---")
st.write("Generated with: emotion mapping + procedural geometry + color psychology.")

