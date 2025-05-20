import speech_recognition as sr

def live_transcription():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Adjusting for ambient noise, please wait...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Ready for speech input...")

    while True:
        try:
            with microphone as source:
                print("Listening...")
                audio = recognizer.listen(source)
                print("Recognizing...")
                transcription = recognizer.recognize_google(audio)
                print(f"Transcription: {transcription}")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    live_transcription()