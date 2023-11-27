import os
import datetime
import openai
import requests
import json
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants for file paths
CHAT_HISTORY_FILE = "C:/Users/miket/OneDrive/Documents/Projects/SongFinder/playlistCurator/chat_history.txt"
SONGS_FILE = "C:/Users/miket/OneDrive/Documents/Projects/SongFinder/playlistCurator/songs.txt"
class Helper_Obj:
    def __init__(self) -> None:
        pass


class ChatGPT_Obj:
    def __init__(self):
        self.message_history = []

    def chat(self, inp, role="user"):
        # Append user input to the message history
        self.message_history.append({"role": role, "content": inp})

        # Call OpenAI's ChatCompletion API
        reply = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.message_history
        )

        # Extract the content of the assistant's reply
        reply_content = reply.choices[0].message.content
        print(reply_content)

        # Append assistant's reply to the message history
        self.message_history.append({"role": "assistant", "content": reply_content})
        return reply_content

    def get_user_input(self):
        while True:
            # Get user input from the console
            user_input = input(">: ")
            print(f"User's input was: {user_input}\n")

            # Continue the conversation until the user inputs "Done"
            if user_input.lower() == "done":
                break

            # Call the chat method to get the assistant's reply
            self.chat(user_input)

class Spotify_Obj:
    def __init__(self):
        self.access_token = None
        self.access_token_expires = datetime.datetime.now()
        self.access_token_did_expire = True
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.token_url = "https://accounts.spotify.com/api/token"

    def get_client_credentials(self):
        """
        Returns a base64 encoded string.
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if not client_id or not client_secret:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in the environment.")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
        return client_creds_b64

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self):
        return {"grant_type": "client_credentials"}

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()

        # Perform authentication with Spotify API
        response = requests.post(token_url, data=token_data, headers=token_headers)

        if response.status_code not in range(200, 299):
            return False

        data = response.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)

        # Update access token information
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def store(self, content, file_path):
        # Store content in a file
        with open(file_path, 'w') as file:
            file.write(content)

    def read(self, file_path):
        # Read content from the stored file
        songs = {}

        with open(file_path) as file:
            for line in file:
                # Split the line into song and artist
                song, artist = map(str.strip, line.split("by"))
                # Add the song and artist to the dictionary
                songs[song.split('. ')[-1].replace('"', '')] = artist

        print(songs)

    def create_playlist(self, name):
        # Create a new playlist on Spotify
        request_body = json.dumps({
            "name": name,
            "description": "New playlist description",
            "public": False
        })

        query = f"https://api.spotify.com/v1/users/{self.client_id}/playlists"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.post(query, data=request_body, headers=headers)
        response_json = response.json()

        # Return the playlist id
        return response_json["id"]

    def search_song(self, songs):
        # Placeholder for the song search functionality
        pass

# Main program
if __name__ == "__main__":
    # Instantiate ChatGPT_API and get user input
    gpt = ChatGPT_Obj()
    gpt.get_user_input()

    # Instantiate SpotifyAPI and perform authentication
    spotify_client = Spotify_Obj()
    print(spotify_client.perform_auth())
    print(spotify_client.access_token)

    # Store GPT's reply content and read stored songs
    spotify_client.store(gpt.message_history[-1]["content"], CHAT_HISTORY_FILE)
    spotify_client.read(SONGS_FILE)