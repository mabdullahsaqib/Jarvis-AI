import threading
import speech
import music
import gemini
from gui import show_gui
import speech_recognition as sr

# Initialize the speech synthesis engine
speaker = speech.initialize_speaker()

# Global flag to stop speaking
stop_speaking = threading.Event()

def main():
    speech.speak("Hello, How can I help you?", speaker)
    while True:
        text = speech.listen()
        if text is None:
            continue
        if "exit" in text.lower():
            speech.speak("Goodbye!", speaker)
            break
        elif any(cmd in text.lower() for cmd in ["play", "pause", "resume", "loop"]):
            music.handle_music_command(text.lower(), speaker)
        else:
            raw_response = gemini.chat.send_message(text)
            # Remove all asterisks from the response text
            response = raw_response.text.replace('*', '')
            while True:
                interruption = speech.speak_with_interrupt(response, speaker)
                if interruption:
                    if "exit" in interruption.lower():
                        speech.speak("Goodbye!", speaker)
                        return
                    else:
                        # Handle the new user input
                        raw_response = gemini.chat.send_message(interruption)
                        # Remove all asterisks from the response text
                        response = raw_response.text.replace('*', '')
                        # Speak the new response with possibility of further interruption
                        interruption = speech.speak_with_interrupt(response, speaker)
                        if interruption:
                            continue  # Handle nested interruptions
                else:
                    break

def detect_wake_word():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for wake word...")

        while True:
            try:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                if "jarvis" in text.lower() or "hey jarvis" in text.lower():
                    print(f"Wake word detected: {text}")
                    show_gui()
                    break
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Error: {e}")
                break

    main()

if __name__ == "__main__":
    wake_word_thread = threading.Thread(target=detect_wake_word)
    wake_word_thread.start()