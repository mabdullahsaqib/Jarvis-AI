import vlc
import threading
import requests
from config import config
import speech

# Global variable to control music playback
playback_control = {
    'play': threading.Event(),
    'loop': False
}

# Function to search for a song on Deezer and return the preview URL
def search_song(query):
    querystring = {"q": query}
    response = requests.get(config.DEEZER_API_URL, headers={
        "x-rapidapi-key": config.X_RAPIDAPI_KEY,
        "x-rapidapi-host": config.X_RAPIDAPI_HOST
    }, params=querystring)
    if response.status_code == 200:
        results = response.json()
        if 'data' in results and results['data']:
            return results['data'][0]['preview']
    return None

# Function to play audio from a URL
def play_audio(url):
    player = vlc.MediaPlayer(url)
    player.play()  # Start playback

    while playback_control['play'].is_set():
        if not playback_control['loop'] and player.get_state() == vlc.State.Ended:
            break

    player.stop()

# Function to handle music commands
def handle_music_command(command, speaker):
    global playback_control
    if 'play' in command:
        query = command.replace('play', '').strip()
        preview_url = search_song(query)
        if preview_url:
            speech.speak(f"Playing {query}", speaker)
            playback_control['play'].set()
            playback_thread = threading.Thread(target=play_audio, args=(preview_url,))
            playback_thread.start()
        else:
            speech.speak("I couldn't find the song.", speaker)
    elif 'pause' in command:
        playback_control['play'].clear()
        speech.speak("Music paused.", speaker)
    elif 'resume' in command:
        playback_control['play'].set()
        speech.speak("Resuming music.", speaker)
    elif 'loop' in command:
        playback_control['loop'] = not playback_control['loop']
        speech.speak("Looping is " + ("enabled." if playback_control['loop'] else "disabled."), speaker)
