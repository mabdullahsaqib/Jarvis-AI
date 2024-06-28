import os
import vlc
import threading
import requests
from dotenv import load_dotenv
import speech_recognition as sr
import win32com.client as wc
import google.generativeai as genai


# Load environment variables from a .env file
load_dotenv()

# Initialize the speech synthesis engine
speaker = wc.Dispatch("SAPI.SpVoice")
voices = speaker.GetVoices()
speaker.Voice = voices.Item(1)
speaker.Rate = 3  # Adjust speech rate (1 = normal speed, 2 = double speed, etc.)

# Configure the generative AI model with the API key from environment variables
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction=os.getenv('JARVIS_MODEL_CONFIG'),
)

# Start a chat session with the generative AI model
chat = model.start_chat(history=[])

# Global flag to stop speaking
stop_speaking = threading.Event()

# Deezer API details
DEEZER_API_URL = os.getenv('DEEZER_API_URL')
DEEZER_HEADERS = {
    "x-rapidapi-key": os.getenv('X-RAPIDAPI_KEY'),
    "x-rapidapi-host": os.getenv('X-RAPIDAPI_HOST')
}

# Function to listen to user input via microphone and convert it to text
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

# Function to convert text to speech with interruption support
def speak(text):
    sentences = text.split('\n')
    for sentence in sentences:
        if stop_speaking.is_set():
            break
        speaker.Speak(sentence)
    print(f"AI: {' '.join(sentences)}")

# Threaded function to handle speaking and allow interruption
def speak_with_interrupt(text):
    global stop_speaking
    stop_speaking.clear()  # Clear the stop_speaking flag

    def speak_thread():
        speak(text)  # Function to perform speaking in a separate thread

    t = threading.Thread(target=speak_thread)  # Create a new thread for speaking
    t.start()  # Start the speaking thread

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        while t.is_alive():  # Check if the speaking thread is still alive
            print("Listening for interruption...")
            try:
                audio = recognizer.listen(source, timeout=1)
                user_input = recognizer.recognize_google(audio)
                if user_input:  # If user input is detected
                    stop_speaking.set()  # Set the flag to stop speaking
                    print(f"User interrupted: {user_input}")
                    t.join()  # Wait for the speak_thread to finish
                    return user_input  # Return the user input
            except sr.WaitTimeoutError:
                # Timeout occurred, continue listening
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Error: {e}")
                break

    t.join()  # Ensure the thread finishes if no interruption occurs
    return None

# Function to search for a song on Deezer
def search_song(query):
    querystring = {"q": query}
    response = requests.get(DEEZER_API_URL, headers=DEEZER_HEADERS, params=querystring)
    if response.status_code == 200:
        results = response.json()
        if 'data' in results and results['data']:
            return results['data'][0]['preview']
    return None

# Global variable to control music playback
playback_control = {
    'play': threading.Event(),
    'pause': threading.Event(),
    'loop': False
}

# Function to play audio from a URL
def play_audio(url):
    p = vlc.MediaPlayer(url)
    p.play()


# Function to handle music commands
def handle_music_command(command):
    if 'play' in command:
        query = command.replace('play', '').strip()
        preview_url = search_song(query)
        if preview_url:
            speak(f"Playing {query}")
            playback_thread = threading.Thread(target=play_audio, args=(preview_url,))
            playback_thread.start()
        else:
            speak("I couldn't find the song.")
    elif 'pause' in command:
        playback_control['play'].clear()
        playback_control['pause'].set()
        speak("Music paused.")
    elif 'resume' in command:
        playback_control['play'].set()
        playback_control['pause'].clear()
        speak("Resuming music.")
    elif 'loop' in command:
        playback_control['loop'] = not playback_control['loop']
        speak("Looping is " + ("enabled." if playback_control['loop'] else "disabled."))
    elif 'stop' in command:
        playback_control['play'].clear()
        playback_control['pause'].clear()
        playback_control['loop'] = False
        speak("Music stopped.")

def main():
    speak("Hello, How can I help you?")
    while True:
        text = listen()
        if text is None:
            continue
        if "exit" in text.lower():
            speak("Goodbye!")
            break
        elif "play" in text.lower() or "pause" in text.lower() or "resume" in text.lower() or "loop" in text.lower() or "stop" in text.lower():
            handle_music_command(text.lower())
        else:
            raw_response = chat.send_message(text)
            # Remove all asterisks from the response text
            response = raw_response.text.replace('*', '')
            while True:
                interruption = speak_with_interrupt(response)
                if interruption:
                    if "exit" in interruption.lower():
                        speak("Goodbye!")
                        return
                    else:
                        # Handle the new user input
                        raw_response = chat.send_message(interruption)
                        # Remove all asterisks from the response text
                        response = raw_response.text.replace('*', '')
                        # Speak the new response with possibility of further interruption
                        interruption = speak_with_interrupt(response)
                        if interruption:
                            continue  # Handle nested interruptions
                else:
                    break

# Check if the script is being run directly
if __name__ == "__main__":
    main()
