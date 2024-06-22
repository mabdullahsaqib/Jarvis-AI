import os
from dotenv import load_dotenv
import speech_recognition as sr
import win32com.client as wc
import google.generativeai as genai

load_dotenv()
speaker = wc.Dispatch("SAPI.SpVoice")
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

chat = model.start_chat(history=[])

#add comments to code
def listen():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"User: {text}")
        return text
    except sr.UnknownValueError:
        print("I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Error: {e}")
    return None


def speak(text):
    speaker.Speak(text)
    print(f"AI: {text}")

def main():
    speak("Hello, I am Gemini. How can I help you today?")
    while True:
        text = listen()
        if text is None:
            continue
        if text == "exit":
            speak("Goodbye!")
            break
        response = chat.send_message(text)
        speak(response.text)


if __name__ == "__main__":
    main()
