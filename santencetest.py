import spacy
import re

nlp = spacy.load("en_core_web_sm")

def parse_command(command):
    # Process the command
    doc = nlp(command.lower())  # Lowercasing makes processing easier

    # List of common music-related verbs
    music_verbs = {"play", "turn on", "start"}

    action = None
    command_start = None

    # Find where the command (e.g., "play") appears
    for token in doc:
        if token.lemma_ in music_verbs:
            action = token.lemma_
            command_start = token.i  # Get index of the command verb
            break  # Stop at the first found command

    if not action:
        return None, None  # No valid command detected

    # Extract song name intelligently
    song_name = None

    # Look for specific phrases like "the song name is"
    song_match = re.search(r"the song'?s? name (?:is|:)\s*(.*?)(?: and |\.|$)", command)
    if song_match:
        song_name = song_match.group(1).strip()

    # If no match, look for a quoted song name
    if not song_name:
        quote_match = re.search(r"['\"](.*?)['\"]", command)
        if quote_match:
            song_name = quote_match.group(1).strip()

    # If no match, assume the song name is the text after "play" but filter it
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

    return action, song_name

# Example test cases
commands = [
    "Good morning Jarvis, I would like and appreciate it if you could please play one of my favorite songs on Spotify, the song's name is Satanized and it's made by Ghost. its like mmy fav so like I would really appricate it if you could play it! thank you so so much I really like this other song by ghost, its called mary on a cross, you should play it after",
    "Can you please play 'Bohemian Rhapsody' by Queen?",
    "Turn on Never Gonna Give You Up by Rick Astley.",
    "Start playing 'Hotel California' from The Eagles.",
    "Play my favorite song, it's called Thunderstruck by AC/DC."
]

for command in commands:
    action, song = parse_command(command)
    print(f"Input: {command}")
    print(f"Action: {action}")
    print(f"Song Name: {song}\n")
