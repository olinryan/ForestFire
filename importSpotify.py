
import json 
import spotipy 
import webbrowser

from dotenv import load_dotenv
import os

# Load .env file into environment variables
load_dotenv()
# To print the response in readable format. 
# print(json.dumps(user_name, sort_keys=True, indent=4)) 

def getSpotifyPlaying(display=False):

    username = os.getenv('SPOTIFY_USERNAME')
    clientID = os.getenv('SPOTIFY_API_KEY')
    clientSecret = os.getenv('SPOTIFY_SECRET')
    redirect_uri = 'http://google.com/callback/'

    oauth_object = spotipy.SpotifyOAuth(clientID, clientSecret, redirect_uri,scope='user-read-playback-state user-library-read') 
    token_dict = oauth_object.get_cached_token() 
    token = token_dict['access_token'] 
    spotifyObject = spotipy.Spotify(auth=token) 
    user_name = spotifyObject.current_user() 
    # Current track
    current_track = spotifyObject.currently_playing()
    if current_track is not None:
        # user name
        user_name = spotifyObject.current_user() ['display_name']
        current_track = spotifyObject.currently_playing()
        track_id = current_track['item']['id']
        artists = current_track['item']['artists']
        if len(artists) == 1:
            artist_name = artists[0]['name']
        else:
            artist_name = ', '.join([artist['name'] for artist in artists])

        progressTime = current_track["progress_ms"]
        totalTime = current_track['item']['duration_ms']

        if display:
            print(f"\nUser: {user_name}")
            # Current track
            print(f"Currently listening too: {current_track['item']['name']}")
            print(f'Track ID: {track_id}')

            # Current Artist
            print(f'Artist(s): {artist_name}')
            
            # Time Stamp
            seconds = (progressTime // 1000) % 60
            minutes = (progressTime // (1000 * 60)) % 60
            print(f"Timestamp {minutes:02}:{seconds:02}")
            seconds = (totalTime // 1000) % 60
            minutes = (totalTime // (1000 * 60)) % 60
            print(f"\t\t of {minutes:02}:{seconds:02}")
            print(spotifyObject.audio_analysis(current_track))
        
        return {"User":user_name,"Track":current_track['item']['name'],"TrackID":track_id,"Artist":artist_name,"TrackLength":totalTime,"CurrentTime":progressTime}

    else:
        return None

