# import necessary modules
import time, json, requests
import spotipy, os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from flask import Flask, request, url_for, session, redirect
load_dotenv()

class SpotifyApp:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")

        self.app = Flask(__name__)
        self.app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
        self.app.secret_key = 'iaknkjfuf982jkf'
        self.TOKEN_INFO = 'token_info'

        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.client_id, client_secret=self.client_secret
        )

        self.app.route('/')(self.login)
        self.app.route('/redirect')(self.redirect_page)
        self.app.route('/createPlaylist')(self.create_playlist)

    def run(self):
        self.app.run(debug=True)

    def login(self):
        try:
            auth_url = self.create_spotify_oauth().get_authorize_url()
            return redirect(auth_url)
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return "Error during login"

    def redirect_page(self):
        try:
            session.clear()
            code = request.args.get('code')
            token_info = self.create_spotify_oauth().get_access_token(code)
            session[self.TOKEN_INFO] = token_info

            user_info = self.get_user_info(token_info['access_token'])
            session['user_id'] = user_info['id']

            return redirect(url_for('create_playlist', external=True))
        except Exception as e:
            print(f"Error during redirect: {str(e)}")
            return "Error during redirect"

    def create_playlist(self):
        try:
            token_info = self.get_token()
        except:
            print("User not logged in")
            return redirect('/')

        playlist_name = input("What would you like to name the playlist?\n")
        user_id = session.get('user_id', None)

        requestBody = json.dumps({
                "name": playlist_name,
                "description": "AI_Generated playlist",
                "public": True
            })
        
        query = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        

        response = requests.post(
            query,
            data=requestBody,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token_info['access_token']}"
            }
        )
        response_json = response.json()
        self.add_songs_to_playlist(response_json["id"])

        return "Successful"

    def add_songs_to_playlist(self, playlist_id):
        songs = [
            {"name": "Sicko Mode", "artist": "Travis Scott"},
            {"name": "Mask Off", "artist": "Future"},
            {"name": "Bad and Boujee", "artist": "Migos"},
            {"name": "Love Sosa", "artist": "Chief Keef"},
            {"name": "Stir Fry", "artist": "Migos"},
            {"name": "Pick Up the Phone", "artist": "Young Thug, Travis Scott"},
            {"name": "Versace", "artist": "Migos"},
            {"name": "No Limit", "artist": "G-Eazy, A$AP Rocky, Cardi B"},
            {"name": "Gucci Gang", "artist": "Lil Pump"},
            {"name": "Powerglide", "artist": "Rae Sremmurd, Juicy J"}
            ]


        sp = spotipy.Spotify(client_credentials_manager= self.client_credentials_manager)

        for entry in songs:
            song_name = entry["name"]
            artist_name = entry["artist"]

            # Example: Search for a track with both song name and artist
            results = sp.search(q=f"track:{song_name} artist:{artist_name}", type="track", limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_uri = track['uri']
                sp.user_playlist_add_tracks(sp.me()['id'], playlist_id, [track_uri])

    def get_user_info(self, access_token):
        user_info_endpoint = "https://api.spotify.com/v1/me"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(user_info_endpoint, headers=headers)
        user_info = response.json()

        return user_info

    # function to get the token info from the session
    def get_token(self):
        token_info = session.get(self.TOKEN_INFO, None)
        if not token_info:
            # if the token info is not found, redirect the user to the login route
            redirect(url_for('login', _external=False))
        
        # check if the token is expired and refresh it if necessary
        now = int(time.time())

        is_expired = token_info['expires_at'] - now < 60
        if(is_expired):
            spotify_oauth = self.create_spotify_oauth()
            token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

        return token_info

    def create_spotify_oauth(self):
        return SpotifyOAuth(
            client_id = self.client_id,
            client_secret = self.client_secret,
            redirect_uri = url_for('redirect_page', _external=True),
            scope='user-library-read playlist-modify-public playlist-modify-private'
        )
if __name__ == "__main__":
    spotify_app = SpotifyApp()
    spotify_app.run()