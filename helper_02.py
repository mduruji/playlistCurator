# import necessary modules
import time, json, requests
import spotipy, os, dotenv
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect
load_dotenv()

# initialize Flask app
app = Flask(__name__)

# set the name of the session cookie
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

# set a random secret key to sign the cookie
app.secret_key = 'iaknkjfuf982jkf'

# set the key for the token info in the session dictionary
TOKEN_INFO = 'token_info'

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

# route to save the Discover Weekly songs to a playlist
@app.route('/saveDiscoverWeekly')
def save_discover_weekly():

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
        
        userID = "31m7zb6fian3thzhyxhhmekq7rki"

        requestBody = json.dumps({
                "name": "Chat Playlist",
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
        playlist_id = response_json["id"]

        return playlist_id


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
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

app.run(debug=True)