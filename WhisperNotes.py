import streamlit as st
import pyttsx3
import PyPDF2
import whisper
import threading
import wave
import os
import time
import tempfile
import math
import bs4 as bs
import urllib.request
import re
import nltk
import spacy
from nltk.stem import WordNetLemmatizer

# Execute this line if you are running this code for the first time
nltk.download('wordnet')

# Initialize components
text_speech = pyttsx3.init()
lemmatizer = WordNetLemmatizer()
nlp = spacy.load('en_core_web_sm')
is_playing = threading.Event()
is_paused = threading.Event()
audio_file_path = "temp_audio.wav"
model = whisper.load_model("base")

# Streamlit App UI
st.title("WhisperNotes: Your AI-Powered Text & Audio Assistant")

# Sidebar
st.sidebar.header("Choose Your Action")
action = st.sidebar.radio(
    "Select a feature:",
    ("Text-to-Speech", "Speech-to-Text", "Summarization")
)

# --------------------------------------
# Text-to-Speech Feature
# --------------------------------------
if action == "Text-to-Speech":
    st.header("Text-to-Speech")
    
    # Sidebar settings
    st.sidebar.subheader("Speech Settings")
    speech_rate = st.sidebar.slider("Speech Speed (Words per Minute)", 100, 250, 180)
    speech_volume = st.sidebar.slider("Volume", 0.0, 1.0, 1.0)
    
    # Apply settings to TTS engine
    text_speech.setProperty('rate', speech_rate)
    text_speech.setProperty('volume', speech_volume)
    
    # Upload file
    uploaded_file = st.file_uploader("Upload a Text or PDF File", type=["txt", "pdf"])
    text_content = ""

    if uploaded_file is not None:
        try:
            if uploaded_file.type == "text/plain":
                text_content = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text_content = "".join([page.extract_text() for page in pdf_reader.pages])

            st.text_area("Text Content", text_content, height=200)
        except Exception as e:
            st.error(f"Error reading file: {e}")

    # Generate and Play Audio
    if st.button("Generate Audio"):
        if text_content.strip():
            text_speech.save_to_file(text_content, audio_file_path)
            text_speech.runAndWait()
            st.success("Audio file generated.")
        else:
            st.error("No text found to convert to speech.")
    
    # Audio controls
    if st.button("Play"):
        def play_audio(file_path):
            global is_playing, is_paused
            wf = wave.open(file_path, 'rb')
            p = wave.open(file_path, 'rb')
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            is_playing.set()
            is_paused.clear()
            chunk = 1024
            data = wf.readframes(chunk)
            while data and is_playing.is_set():
                if is_paused.is_set():
                    time.sleep(0.1)
                    continue
                stream.write(data)
                data = wf.readframes(chunk)
            stream.stop_stream()
            stream.close()
            p.terminate()
            wf.close()
            is_playing.clear()
        threading.Thread(target=play_audio, args=(audio_file_path,), daemon=True).start()

# Summarized .
    if st.button("Pause"):
        is_paused.set()
    if st.button("Resume"):
        is_paused.clear()
    if st.button("Stop"):
        is_playing.clear()
    if os.path.exists(audio_file_path):
        with open(audio_file_path, "rb") as audio_file:
            st.download_button("Download Audio", data=audio_file, file_name="generated_audio.wav")

# --------------------------------------
# Speech-to-Text Feature
# --------------------------------------
elif action == "Speech-to-Text":
    st.header("Speech-to-Text")
    audio_file = st.file_uploader("Upload an audio file for transcription", type=["wav", "mp3", "m4a"])

    if st.sidebar.button("Transcribe"):
        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_file.read())
                transcription = model.transcribe(temp_audio.name)
                st.text_area("Transcription", transcription["text"], height=200)
        else:
            st.error("Please upload an audio file.")

# --------------------------------------
# Summarization Feature
# --------------------------------------
elif action == "Summarization":
    st.header("Summarization")
    input_type = st.radio("Choose input type:", ("Text", "File", "Wikipedia URL"))
    text = ""

    if input_type == "Text":
        text = st.text_area("Enter your text:", height=200)
    elif input_type == "File":
        file = st.file_uploader("Upload a text or PDF file:", type=["txt", "pdf"])
        if file:
            try:
                if file.type == "text/plain":
                    text = file.read().decode("utf-8")
                elif file.type == "application/pdf":
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = "".join([page.extract_text() for page in pdf_reader.pages])
            except Exception as e:
                st.error(f"Error reading file: {e}")
    elif input_type == "Wikipedia URL":
        url = st.text_input("Enter Wikipedia URL:")
        if st.button("Fetch Content"):
            try:
                article = urllib.request.urlopen(url).read()
                parsed_article = bs.BeautifulSoup(article, 'lxml')
                paragraphs = parsed_article.find_all('p')
                text = " ".join([p.text for p in paragraphs])
            except Exception as e:
                st.error(f"Error fetching article: {e}")

    if text:
        sentences = list(nlp(text).sents)
        freq_matrix = {str(sent): {word.lower_: text.count(word.lower_) for word in sent if word.is_alpha} for sent in sentences}
        sentence_scores = {sent: sum(freq_matrix[str(sent)].values()) for sent in freq_matrix}
        avg_score = sum(sentence_scores.values()) / len(sentence_scores)
        summary = " ".join([str(sent) for sent in sentence_scores if sentence_scores[sent] > 1.3 * avg_score])
        st.text_area("Summary", summary, height=200)
    else:
        st.info("Provide text input to generate a summary.")