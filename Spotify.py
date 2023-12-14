import json, requests, os, base64
from dotenv import load_dotenv
load_dotenv()


class Spotify:
    def __init__(self):
        self.clientID = os.getenv("CLIENT_ID")
        self.clientSecret = os.getenv("CLIENT_SECRET")
        self.userID = "31m7zb6fian3thzhyxhhmekq7rki"
        self.spotifyToken = os.getenv("ACCESS_TOKEN")
        self.token_url = "https://accounts.spotify.com/api/token"
        
    def createPlaylist(self):
        requestBody = json.dumps({
                "name": "Chat Playlist",
                "description": "AI_Generated playlist",
                "public": True
            })
        
        query = f"https://api.spotify.com/v1/users/{self.userID}/playlists"
        

        response = requests.post(
            query,
            data=requestBody,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.spotifyToken}"
            }
        )
        response_json = response.json()
        playlist_id = response_json["id"]


    def getSpotifyUri(self) -> None:
        pass

    def addSongToPlaylist(self) -> None:
        pass

if __name__ == "__main__":
    s = Spotify()
    s.createPlaylist()