import threading
import speech
import music
import gemini
from gui import voice_assistant_gui
import speech_recognition as sr

# Initialize the speech synthesis engine
speaker = speech.initialize_speaker()

# Global flag to stop speaking
stop_speaking = threading.Event()

def main():
    speech.speak("Hello, How can I help you?", speaker)
    while True:
        voice_assistant_gui.set_listening()
        text = speech.listen()
        voice_assistant_gui.stop_animation()
        if text is None:
            continue
        if "exit" in text.lower():
            speech.speak("Goodbye!", speaker)
            voice_assistant_gui.root.quit()  # Close the GUI
            break
        elif any(cmd in text.lower() for cmd in ["play", "pause", "resume", "loop"]):
            music.handle_music_command(text.lower(), speaker)
        else:
            raw_response = gemini.chat.send_message(text)
            # Remove all asterisks from the response text
            response = raw_response.text.replace('*', '')
            while True:
                voice_assistant_gui.set_speaking()
                interruption = speech.speak_with_interrupt(response, speaker)
                voice_assistant_gui.stop_animation()
                if interruption:
                    if "exit" in interruption.lower():
                        speech.speak("Goodbye!", speaker)
                        voice_assistant_gui.root.quit()  # Close the GUI
                        return
                    else:
                        # Handle the new user input
                        raw_response = gemini.chat.send_message(interruption)
                        # Remove all asterisks from the response text
                        response = raw_response.text.replace('*', '')
                        # Speak the new response with possibility of further interruption
                        voice_assistant_gui.set_speaking()
                        interruption = speech.speak_with_interrupt(response, speaker)
                        voice_assistant_gui.stop_animation()
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
                    voice_assistant_gui.show()
                    break
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Error: {e}")
                break
        main()

if __name__ == "__main__":
    detect_wake_word_thread = threading.Thread(target=detect_wake_word)
    detect_wake_word_thread.start()
    voice_assistant_gui.hide()  # Start with GUI hidden
    voice_assistant_gui.run()  # Start the GUI main loop after wake word detection