import streamlit as st
import speech_recognition as sr
from transformers import pipeline
import time

# Initialize the recognizer and summarizer
recognizer = sr.Recognizer()
summarizer = pipeline("summarization")

# Function to transcribe speech
def transcribe_speech():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            transcription = recognizer.recognize_google(audio)
            return transcription
        except sr.UnknownValueError:
            return "Google Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"

# Streamlit app
st.title("Live Speech Transcription and Summarization")

# Initialize session state for transcriptions and listening status
if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = []

if 'listening' not in st.session_state:
    st.session_state.listening = False

def start_listening():
    st.session_state.listening = True

def stop_listening():
    st.session_state.listening = False

def clear_transcriptions():
    st.session_state.transcriptions = []

# Buttons for controlling the listening process
start_button = st.button("Start Listening", on_click=start_listening)
stop_button = st.button("Stop Listening", on_click=stop_listening)
clear_button = st.button("Clear Transcriptions", on_click=clear_transcriptions)

# Placeholders for displaying transcriptions and summaries
transcription_placeholder = st.empty()
summary_placeholder = st.empty()

# Real-time transcriptions display
while st.session_state.listening:
    transcription = transcribe_speech()
    st.session_state.transcriptions.append(transcription)
    
    # Display all transcriptions as they are added
    transcription_placeholder.write("Transcriptions:")
    for i, transcription in enumerate(st.session_state.transcriptions, 1):
        transcription_placeholder.write(f"{i}. {transcription}")
    
    # Add a small delay to avoid overwhelming the recognizer
    time.sleep(1)

# Display all transcriptions after stopping listening and offer the option to summarize
if not st.session_state.listening and st.session_state.transcriptions:
    transcription_placeholder.write("All Transcriptions:")
    for i, transcription in enumerate(st.session_state.transcriptions, 1):
        transcription_placeholder.write(f"{i}. {transcription}")

    # Offer the option to summarize the full transcriptions after stopping
    summarize_button = st.button("Summarize", key="summarize_button")
    if summarize_button:
        full_text = " ".join(st.session_state.transcriptions)
        summary = summarizer(full_text, max_length=50, min_length=25, do_sample=False)[0]['summary_text']
        summary_placeholder.write("Summary:")
        summary_placeholder.write(summary)
