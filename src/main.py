import threading
import speech
import music
import gemini

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

# Check if the script is being run directly
if __name__ == "__main__":
    main()
