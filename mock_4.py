import os, datetime, openai
import requests, json, base64
from dotenv import load_dotenv
load_dotenv()
message_history = []
filename = "C:/Users/miket/OneDrive/Documents/Projects/SongFinder/songs.txt"

class ChatGPT_API(object):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    reply = None
    user_input = None
    reply_content = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def chat(self, inp, role = "user"):
        message_history.append({"role": role,"content": inp})

        reply = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = message_history
        )

        reply_content = reply.choices[0].message.content
        print(reply_content)
        message_history.append({"role":"assistant","content": reply_content})

        self.reply_content = reply_content
        self.message_history = message_history
        return reply_content
    
    def get_user_input(self):
        i = 0
        while (i != 2):
            user_input = input(">: ")
            self.user_input = user_input
            print("User's input was", self.user_input)
            print()
            if(user_input != "Done"):
                self.chat(self.user_input)
            else:
                i = 2
            print()

class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    token_url = "https://accounts.spotify.com/api/token"
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_client_credentials(self):
        """
        returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret == None:
            raise Exception("You must set client id and client secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return{
            "Authorization": f"Basic {client_creds_b64}"
        }
    
    def get_token_data(self):
        return{
            "grant_type": "client_credentials"
        }
    
    
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)

        if r.status_code not in range(200,299):
            return False
        
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True
    
    def store(self, cntnt):
        song_file = open(filename,'w')
        song_file.write(cntnt)
        song_file.close()

    def read(self):
        filename = "songs.txt"
        global songs
        songs = {}

        with open(filename) as file:
            for line in file:
                # split the line into song and artist
                song, artist = line.strip().split("by")
                # add the song and artist to the dictionary

                songs[song.split('. ')[-1].replace('"', '')] = artist

        print(songs)

    
    def createplaylist(self, name):
        request_body = json.dumps({
            "name": name,
            "description": "New playlist description",
            "public": False
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(client.client_id)
        response = requests.post(
            query,
            data = request_body,
            headers ={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(client.access_token)
            }
        )
        response_json = response.json()

        #playlist id
        return response_json["id"]
    
    def searchSong(self, songs):
        
        pass

gpt = ChatGPT_API()
gpt.get_user_input()
client = SpotifyAPI()
"""
print(client.perform_auth())
print(client.access_token)
print(client.client_id)
"""

client.store(gpt.reply_content)
client.read()