# Simple constants
DEFAULT_AMOUNT_OF_SONGS = 1
DEFAULT_AMOUNT_OF_SONGS_TO_SEARCH = 5

# Options
YDL_OPTIONS = {
    'format': 'bestaudio',
    'quiet': True
}

# Youtube URL prefix
YOUTUBE_URL_1 = "youtube.com/watch?"
YOUTUBE_URL_2 = "https://youtu.be"

# Messages
JOIN_NOT_IN_VOICE_CHAT = "You are not currently in a voice channel!\nEnter a channel to start playing some music."
LEAVE_NOT_IN_VOICE_CHAT = "The bot is not connected to any voice channel!"
PLAY_SONG_NOT_INCLUDED = "You haven't specified a song!\nSpecify a song to play with the commands: '-play <song_name>' or '-play <song_url>'"
PLAY_NOT_IN_VOICE_CHAT = "I must be in a voice channel to play a song!"
SEARCH_SONG = "Searching for your song, this may take a few seconds..."
SONG_NOT_FOUND = "Sorry, I could not find the given song, try using the search command."
ADDED_TO_QUEUE = "There is a song currently playing! I've added your song to the end of the queue."
QUEUE_LIMIT = "Sorry, I can only queue up to 10 songs, please wait for the current song to finish."
SEARCH_SONG_NOT_INCLUDED = "You haven't specified a song!\nSpecify a song to search with the commands: '-search <song_name>' or '-search <song_url>'"
SEARCH_DESCRIPTION = "*You can use these URL's to play an exact song if the one you want isn't the first result.*\n"
QUEUE_EMPTY = "The song queue is empty right now."
PAUSED = "Paused ⏸️"
RESUMED = "Resumed ⏯️"
SKIPPED = "Skipped ⏭️"
SKIP_NO_SONG = "I am not playing any song right now."
SKIP_AUTHOR_NOT_CONNECTED = "You are not connected to any voice channel!"
SKIP_AUTHOR_IN_DIFFERENT_CHANNEL = "I am not currently playing any songs for you!"