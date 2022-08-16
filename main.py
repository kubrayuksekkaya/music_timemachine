import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = "https://example.com/callback/"
ENDPOINT = "https://www.billboard.com/charts/hot-100/"

# Scraping Billboard 100

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

response = requests.get(f"{ENDPOINT}{date}")
soup = BeautifulSoup(response.text, 'html.parser')
song_names_spans = soup.select("li h3")
data = [song.getText().strip() for song in song_names_spans]

for n in range(0, 7):
    data.remove(data[-1])

# Spotify Authentication

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=REDIRECT_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
print(user_id)

# Searching Spotify for songs

song_uris = []
year = date.split("-")[0]
for song in data:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Creating a new playlist in Spotify

playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
print(playlist)

# Adding songs into the new playlist

sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
