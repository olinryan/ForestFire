import spotipy
import spotipy.util as util
import json 
import os
import spotipy 
import webbrowser
from dotenv import load_dotenv

# Load .env file into environment variables
load_dotenv()

redirect_url = 'https://google.com/callback/?code=AQB-La1CPzVfRajGAl1j0ia7lYDk8wtrUESHBM_-0eXxwtxcsUmfLT6V9TtI_cI5fKRTgP7qehqNq2fWs_eZ4DjN4WCSFuvw0a1TLMtikiKtVCDutMsQC4QlxNmXpPtK70Uh5t-z2VYG2l0iseafa2xgrhNLSluzyVs-t9YWEA'
 
scope = 'user-read-currently-playing'
# scope = 'user-read-playback-state'
# works as well

# token = util.prompt_for_user_token('SPOTIFY_USERNAME', scope, client_id='SPOTIFY_API_KEY', client_secret='SPOTIFY_SECRET', redirect_uri='https://google.com/callback/?code=AQB-La1CPzVfRajGAl1j0ia7lYDk8wtrUESHBM_-0eXxwtxcsUmfLT6V9TtI_cI5fKRTgP7qehqNq2fWs_eZ4DjN4WCSFuvw0a1TLMtikiKtVCDutMsQC4QlxNmXpPtK70Uh5t-z2VYG2l0iseafa2xgrhNLSluzyVs-t9YWEA')

spotify = spotipy.Spotify(auth=token)
current_track = spotify.current_user_playing_track()

print(current_track)