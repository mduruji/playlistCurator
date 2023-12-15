# import necessary modules
import time, json, requests
import spotipy, os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from flask import Flask, request, url_for, session, redirect
load_dotenv()

clientID = os.getenv("CLIENT_ID")
clientSecret = os.getenv("CLIENT_SECRET")
userID = "31m7zb6fian3thzhyxhhmekq7rki"
# initialize Flask app
app = Flask(__name__)

# set the name of the session cookie
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

# set a random secret key to sign the cookie
app.secret_key = 'iaknkjfuf982jkf'

# set the key for the token info in the session dictionary
TOKEN_INFO = 'token_info'

#create a spotify client credentials manager
client_credentials_manager = SpotifyClientCredentials(client_id=clientID, client_secret=clientSecret)
# route to handle logging in
@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

# route to handle the redirect URI after authorization
@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('create_playlist', external = True))

    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/')
    return token_info
    
@app.route('/createPlaylist')
def create_playlist():
        try:
            token_info = get_token()
        except:
            print("User not logged in")
            return redirect('/')
        
        playlist_name = input("What would you like to name the playlist?\n")

        requestBody = json.dumps({
                "name": playlist_name,
                "description": "AI_Generated playlist",
                "public": True
            })
        
        query = f"https://api.spotify.com/v1/users/{userID}/playlists"
        

        response = requests.post(
            query,
            data=requestBody,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token_info['access_token']}"
            }
        )
        response_json = response.json()
        add_songs_to_playlist(response_json["id"])

        return "Successful"

def add_songs_to_playlist(playlist_id):
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


    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    for entry in songs:
        song_name = entry["name"]
        artist_name = entry["artist"]

        # Example: Search for a track with both song name and artist
        results = sp.search(q=f"track:{song_name} artist:{artist_name}", type="track", limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_uri = track['uri']
            sp.user_playlist_add_tracks(sp.me()['id'], playlist_id, [track_uri])

# function to get the token info from the session
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        # if the token info is not found, redirect the user to the login route
        redirect(url_for('login', _external=False))
    
    # check if the token is expired and refresh it if necessary
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = clientID,
        client_secret = clientSecret,
        redirect_uri = url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

if __name__ == "__main__":
    app.run(debug=True)