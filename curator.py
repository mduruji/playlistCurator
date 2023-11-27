import spotifyOBJ
import chatOBJ
import helper

CHAT_HISTORY_FILE = "C:/Users/miket/OneDrive/Documents/Projects/SongFinder/playlistCurator/chat_history.txt"
SONGS_FILE = "C:/Users/miket/OneDrive/Documents/Projects/SongFinder/playlistCurator/songs.txt"

if __name__ == "__main__":
    # Instantiate ChatGPT_API and get user input
    gpt = chatOBJ.ChatGPT_Obj()
    gpt.get_user_input()

    # Instantiate SpotifyAPI and perform authentication
    spotify_client = spotifyOBJ.Spotify_Obj()
    print(spotify_client.perform_auth())
    print(spotify_client.access_token)

    # Store GPT's reply content and read stored songs
    spotify_client.store(gpt.message_history[-1]["content"], CHAT_HISTORY_FILE)
    spotify_client.read(SONGS_FILE)