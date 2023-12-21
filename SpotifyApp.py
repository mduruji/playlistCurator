import time
import json
import requests
import spotipy
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from flask import Flask, request, url_for, session, redirect

load_dotenv()

class spotifyApp:
    def __init__(self, secret_key, songs):
        """
        Initialize the SpotifyApp object.

        Parameters:
        - secret_key: Secret key for the Flask app.
        - songs: List of dictionaries representing songs with 'name' and 'artist'.
        """
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.songs = songs

        self.app = Flask(__name__)
        self.app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
        self.app.secret_key = secret_key
        self.TOKEN_INFO = 'token_info'

        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=self.client_id, client_secret=self.client_secret
        )

        self.app.route('/')(self.login)
        self.app.route('/redirect')(self.redirect_page)
        self.app.route('/createPlaylist')(self.create_playlist)

    def go(self):
        """Run the Flask app."""
        self.app.run(debug=False)

    def login(self):
        """Handle the login route."""
        try:
            auth_url = self.create_spotify_oauth().get_authorize_url()
            return redirect(auth_url)
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return "Error during login"

    def redirect_page(self):
        """Handle the redirect route after authorization."""
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
        """Handle the createPlaylist route."""
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
        """Add songs to the created playlist."""
        sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)

        for entry in self.songs:
            song_name = entry["name"]
            artist_name = entry["artist"]

            results = sp.search(q=f"track:{song_name} artist:{artist_name}", type="track", limit=1)
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                track_uri = track['uri']
                sp.user_playlist_add_tracks(sp.me()['id'], playlist_id, [track_uri])

    def get_user_info(self, access_token):
        """Get user information using the access token."""
        user_info_endpoint = "https://api.spotify.com/v1/me"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(user_info_endpoint, headers=headers)
        user_info = response.json()

        return user_info

    def get_token(self):
        """Get the token info from the session."""
        token_info = session.get(self.TOKEN_INFO, None)
        if not token_info:
            redirect(url_for('login', _external=False))
        
        now = int(time.time())

        is_expired = token_info['expires_at'] - now < 60
        if is_expired:
            spotify_oauth = self.create_spotify_oauth()
            token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

        return token_info

    def create_spotify_oauth(self):
        """Create and return a SpotifyOAuth object."""
        return SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=url_for('redirect_page', _external=True),
            scope='user-library-read playlist-modify-public playlist-modify-private'
        )