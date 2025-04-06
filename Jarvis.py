import pyttsx3
import sys
import spotipy
import speech_recognition as sr
from random import choice
from datetime import datetime
import threading
import cv2
from PIL import Image
from deepface import DeepFace
#from openAiTest.ArticleSum import sum
from utils import opening_text_female, opening_text_male, waking_up_words
from shortcuts.shortcuts_spotify import SpotifyAddShortcut
from shortcuts.shortcuts_games import GamesShortcuts
from google_Search.google_photo import GoogleImageDownloader
from google_Search.google_search import GoogleCustomSearch
import json
from rating.rating import RatingClass
from face.face import FaceCapture
import webbrowser
from Functions.online_ops import (
    find_my_ip, get_random_joke, search_on_google, search_on_wikipedia, send_whatsapp_messege,
    play_youtube, send_whatsapp_image
)
from Functions.os_ops import (
    open_calculator, open_camera, open_cmd, open_discord, open_notepad, enter_number
)
from decouple import config
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import os
import spacy
import re


query = None
chatbot_response = None

# Initialize pyttsx3 engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Select a male voice (if available)
for voice in voices:
    if "male" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from bot.JarvisBot import *
#spotify


username = 'Bred'
clientID = 'e11ef3f72cda44ffba398aaf5fcc197b'
clientSecret = '7169a5e1ffb744f29d8eaf6cb20e18b3'
redirect_uri = 'http://google.com/callback/'


oauth_object = spotipy.SpotifyOAuth(clientID, clientSecret, redirect_uri) 
token_dict = oauth_object.get_access_token() 
token = token_dict['access_token'] 
spotifyObject = spotipy.Spotify(auth=token) 
user_name = spotifyObject.current_user() 


nlp = spacy.load("en_core_web_sm")

def get_music_command(command):
    """
    Extracts the action and song name from a natural language command.
    
    :param command: User input as a string.
    :return: Dictionary with 'action' and 'song_name'.
    """
    # Process command with spaCy
    doc = nlp(command.lower())  # Lowercase for easier matching

    # Common verbs related to music commands
    music_verbs = {"play", "turn on", "start"}

    action = None
    command_start = None

    # Find the command verb (e.g., "play", "start")
    for token in doc:
        if token.lemma_ in music_verbs:
            action = token.lemma_
            command_start = token.i  # Store the index of the verb
            break  # Stop at the first found command

    if not action:
        return {"action": None, "song_name": None}  # No valid command detected

    # Extract song name
    song_name = None

    # Look for "the song name is" or similar phrases
    song_match = re.search(r"the song'?s? name (?:is|:)\s*(.*?)(?: and |\.|$)", command)
    if song_match:
        song_name = song_match.group(1).strip()

    # Look for quoted song name
    if not song_name:
        quote_match = re.search(r"['\"](.*?)['\"]", command)
        if quote_match:
            song_name = quote_match.group(1).strip()

    # If no match, assume the song name is the text after "play"
    if not song_name and command_start is not None:
        words_after_play = command.split()[command_start + 1:]

        # Stop if we hit "on Spotify", "by", or similar phrases
        stop_words = {"on", "by", "from", "in", "with"}
        filtered_words = []
        for word in words_after_play:
            if word in stop_words:
                break
            filtered_words.append(word)

        song_name = " ".join(filtered_words).strip()

    return {"action": action, "song_name": song_name}

def play_on_spotify(song_name):
    """Searches for the song on Spotify and plays it."""
    if not song_name:
        speak("I couldn't find a song name. Please try again.")
        return

    results = spotifyObject.search(song_name, 1, 0, "track")
    songs_dict = results.get('tracks', {})
    song_items = songs_dict.get('items', [])

    if not song_items:
        speak(f"Sorry, I couldn't find the song {song_name} on Spotify.")
        return

    song_url = song_items[0]['external_urls']['spotify']
    webbrowser.open(song_url)
    speak(f"Playing {song_name} on Spotify.")
    print("Song has opened in your browser.")
#spotify end


#huggingface login
email = "danielbartal2102@gmail.com"
password = "Danielbartal21"
jarvis_bot = JarvisChatBot(email, password)
example = ""

#search photos
api_key_photo = "AIzaSyBdNnlYzQVjuPiEtDqRUGhOyLhWRAw00gU"
cx_photo = "b0ef57416009643e5"
downloader = GoogleImageDownloader(api_key_photo, cx_photo)

#google search

api_key_search = "AIzaSyBdNnlYzQVjuPiEtDqRUGhOyLhWRAw00gU"
cx_search = "0782d58f2626148c6"
google_search = GoogleCustomSearch(api_key_search, cx_search)

#search

BotName = "Jarvis".lower()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
min_volume, max_volume, _ = volume.GetVolumeRange()

lang = 'en'
face_match = "False"

#memory

MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "short_term_memory": [],
            "long_term_memory": {
                "favorite_topics": [],
                "important_facts": {},
                "interaction_history": []
            }
        }  # Default memory structure




'''
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

daniel = cv2.imread("daniel.png")
idan = cv2.imread("idan.png")
sarah = cv2.imread("sarah.png")

def check_face(frame):
    global face_match
    try:
        if DeepFace.verify(frame, idan.copy())['verified']:
            face_match = "Idan"
        elif DeepFace.verify(frame, daniel.copy())['verified']:
            face_match = "Daniel"
        elif DeepFace.verify(frame, sarah.copy())['verified']:
            face_match = "Sarah"
    except Exception as e:
        print(f"Error in face verification: {e}")

counter = 0
whosOn = "False"
while True:
    ret, frame = cap.read()
    if ret:
        if counter % 30 == 0:
            threading.Thread(target=check_face, args=(frame.copy(),)).start()
        counter += 1

        if face_match in ["Daniel", "Idan", "Sarah"]:
            cv2.putText(frame, face_match, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            whosOn = face_match
            counter = 0
            break
        else:
            cv2.putText(frame, "NO MATCH", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)

        cv2.imshow("video", frame)

    if cv2.waitKey(1) == ord("q"):
        whosOn = "False"
        break

cap.release()
cv2.destroyAllWindows()
'''
def get_prononuce(user_name):
        try:
            with open(f"{user_name}_pronounce.txt", "r") as file:
                print("read")
                pronounce = file.read()
                return pronounce
        except FileNotFoundError:
            return None
        

#face_capture = FaceCapture()
#recognized_user = face_capture.recognize_user()
#whosOn = recognized_user
#pronounce = get_prononuce(whosOn)

engine.setProperty('rate', 190)
engine.setProperty('volume', 1.0)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def greet_user():
    hour = datetime.now().hour
    if 6 <= hour < 12:
        speak(f"Good morning {whosOn}.")
    elif 12 <= hour < 16:
        speak(f"Good afternoon {whosOn}.")
    elif 16 <= hour < 19:
        speak(f"Good evening {whosOn}.")
    speak(f"How may I assist you?")

keywords = ['search', 'open', 'start']

def take_user_input(jarvis_chatbot):
    """Captures user voice input and processes commands."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-us')
    except Exception:
        speak("Sorry, I didn't understand that. Can you please repeat?")
        return take_user_input(jarvis_chatbot)

    # Check for exit command
    if 'exit' in query or 'stop' in query:
        
        return 'exit'

    chatbot_response = jarvis_chatbot.send_message(query)
    speak(chatbot_response)
    # Convert number words to integers
    num_map = {
        "one": 1, "two": 2, "three": 3,
        "four": 4, "five": 5, "six": 6
    }
    if query in num_map:
        query = num_map[query]

    # Process music-related commands
    music_command = get_music_command(query)
    if music_command["action"] == "play" and music_command["song_name"]:
        play_on_spotify(music_command["song_name"])
        

    # Send query to chatbot
    

    return query


def take_user_input2():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-us')
    except Exception:
        query = 'None'
    return query

if __name__ == '__main__':
    
    face_capture = FaceCapture()
    recognized_user = face_capture.recognize_user()
    print(f"User recognized as: {recognized_user}")
    
    if recognized_user != "Unknown":
        pronounce = face_capture.get_pronounce(recognized_user)
        print(f"Pronunciation for {recognized_user}: {pronounce}")
        whosOn = recognized_user
    else:
        print("No user recognized.")
    
    while True:
        print('h')
        awake = False
        query = take_user_input(jarvis_bot).lower()
        if not awake and any(wakeUp in query.lower() for wakeUp in waking_up_words):
            print (f"{awake} 1")
            awake = True
            print(f"{awake} 2")
            greet_user()
            while 'stop' not in query or 'exit' not in query:
                
                query = take_user_input(jarvis_bot).lower()
                said = jarvis_bot.send_message(query)
                jarvis_bot = JarvisChatBot(email, password, query, said)
                if query == 'exit':
                    break
                if 'notepad' in query and any(keyword in query.lower() for keyword in keywords): #if one of the keywords appear in query with notepad
                    open_notepad()
                    example = "Opening notepad Or starting notepad right now..."
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                elif 'discord' in query and any(keyword in query.lower() for keyword in keywords):
                    open_discord()
                    example = "Opening discord Or starting discord right now..."
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                elif 'command prompt' in query or 'cmd' in query and any(keyword in query.lower() for keyword in keywords):
                    open_cmd()
                    example = "Opening cmd / command prompt Or starting cmd / command promt right now..."
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                elif 'camera' in query and any(keyword in query.lower() for keyword in keywords):
                    open_camera()
                    example = "Opening your camera Or starting camera right now..."
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                elif 'calculator' in query and any(keyword in query.lower() for keyword in keywords):
                    open_calculator()
                    example = "Opening the calculator..."
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                elif 'ip address' in query:
                    ip_address = find_my_ip()
                    example(f'Your IP address is {ip_address}. I will print it on the screen, {pronounce}.')
                    print(f'Your IP address is: {ip_address}')
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                elif 'wikipedia' in query and 'search' in query:
                    example(f'What do you want to search for, {pronounce}? and then I give you what I wanna search')
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                    search_query = take_user_input(jarvis_bot).lower()
                    results = search_on_wikipedia(search_query)
                    example(f"According to Wikipedia, {results} I am printing it on the screen, {pronounce}.")
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                    print(results)
                elif 'youtube' in query and 'search' in query or 'watch' in query:
                    example(f'What do you want to watch, {pronounce}?')
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                    video = take_user_input(jarvis_bot).lower()
                    play_youtube(video)
                elif 'google' in query and 'search':
                    example(f'What do you want to search for, {pronounce}? and then im giving you what I wanna search...')
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                    search_query = take_user_input(jarvis_bot)
                    search_results = google_search.fetch_results(search_query)
                    google_search.print_results()
                    query = take_user_input(jarvis_bot)
                    if query.lower().startswith('open '):
                        try:
                            num = int(query.split(' ')[1])
                            google_search.open_result(num)
                        except ValueError:
                            speak("Please provide a valid number after 'open'.")
                    
                elif 'whatsapp' in query and 'message' in query and 'send' in query:
                    example(f'Do you want to say the name, {pronounce}? and then you are waiting for a yes or no answer from me')
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                    response = take_user_input(jarvis_bot).lower()
                    if 'yes' in response:
                        example(f'(if I said yes) What is the name, {pronounce}?')
                        jarvis_bot = JarvisChatBot(email, password, query, said, example)
                        name = take_user_input(jarvis_bot).lower()
                        number = 0
                    else:
                        example(f'(if I said no) To which number do you want to send a message, {pronounce}?')
                        jarvis_bot = JarvisChatBot(email, password, query, said, example)
                        number = input("Enter the number: ")
                        name = 'none'
                    example(f"(you got the number / name) What is the message, {pronounce}?")
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                    message = take_user_input(jarvis_bot).lower()
                    send_whatsapp_messege(name, number, message)
                    example(f"I've sent the message, {pronounce}.")
                elif 'whatsapp' in query and 'photo' in query and 'send' in query:
                    speak(f'Do you want to say the name, {pronounce}?')
                    response = take_user_input(jarvis_bot).lower()
                    if 'yes' in response:
                        speak(f'What is the name, {pronounce}?')
                        name = take_user_input(jarvis_bot).lower()
                        number = 0
                    else:
                        speak(f'To which number do you want to send a message, {pronounce}?')
                        number = input("Enter the number: ")
                        name = 'none'
                    speak(f"Please choose the photo you want to send, {pronounce}.")
                    speak(f"What do you want to say with that photo, {pronounce}?")
                    message = take_user_input(jarvis_bot).lower()
                    send_whatsapp_image(name, number, message)
                    speak(f"I've sent the message, {pronounce}.")
                elif 'joke' in query:
                    example(f"Here is a joke for you, {pronounce}. Hope you like this one.")
                    joke = get_random_joke()
                    jarvis_bot = JarvisChatBot(email, password, query, said, example,joke)
                    
                
                elif 'play' in query and 'game' in query:
                    example(f"What do you want to play {pronounce}?")
                    jarvis_bot = JarvisChatBot(email, password, query, said, example)
                    game = take_user_input()
                    game_shortcuts = GamesShortcuts()
                    if game not in game_shortcuts.get_shortCut():
                        game_shortcuts.add_path(game, "")
                        example(f" (if the game is not in the file I need to add the path) {game} added {pronounce}, please put the path in the chat.")
                        jarvis_bot = JarvisChatBot(email, password, query, said, example)
                        path = input("PATH: ")
                        game_shortcuts.add_path(game, path)
                    else:
                        example(f"starting {game}, ENJOY!")
                        jarvis_bot = JarvisChatBot(email, password, query, said, example)
                        os.startfile(path)
                
                elif 'search' in query and ('image' in query or 'photo'):
                    
                    speak("What do you want to search?")
                    search = take_user_input()
                    
                    downloader.download_images(search)

                elif 'open' in query and ('image' in query or 'photo' in query):
                    speak(f"Which photo do you want to open {pronounce}")
                    photo = take_user_input()
                    speak("which number do you want?")
                    number = take_user_input()
                    downloader.open_image(f"{photo}_{number}")
                elif 'new' in query and 'user' in query:
                    face_capture.run()
                elif 'check' in query:
                    rating = RatingClass()
                    rating.check_rating()
                elif any(wakeUp in query.lower() for wakeUp in waking_up_words):
                    if awake:
                        speak(f"Yes, {pronounce}, I am awake and ready. Do you need anything?")
                    else:
                        speak(f"I am awake now {pronounce}, anything you need?")
                
            
                    
