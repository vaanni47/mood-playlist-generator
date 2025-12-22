import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

# 1. Load your secrets
load_dotenv()

client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

# 2. Setup Authentication
scope = "playlist-modify-public user-top-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
))

# 3. Verify Connection
user = sp.current_user()
print(f"\n--- Connected as: {user['display_name']} ---")

# 4. Interactive Input
mood = input("\nHow are you feeling today? (happy, sad, chill, workout): ").lower()

# 5. Search Map (Global + Bollywood specific keywords)
search_map = {
    "happy":  ["happy upbeat pop 2025", "bollywood party hits", "bhangra dance"],
    "sad":    ["sad melancholic acoustic", "hindi sad songs", "emotional bollywood"],
    "chill":  ["lofi chill study beats", "bollywood lofi", "hindi acoustic"],
    "workout": ["high energy gym phonk", "bollywood workout beats", "punjabi gym"]
}

queries = search_map.get(mood, ["chill hits", "bollywood chill"])
all_track_uris = []

print(f"Searching for a mix of global and Bollywood {mood} tracks...")

# 6. Loop through multiple queries to get a mix
for query in queries:
    # We search for a playlist first
    search_results = sp.search(q=query, type='playlist', limit=1)
    if search_results['playlists']['items']:
        playlist_id = search_results['playlists']['items'][0]['id']
        
        # Pull 20 tracks from this playlist (increased limit!)
        tracks = sp.playlist_items(playlist_id, limit=20)
        uris = [item['track']['uri'] for item in tracks['items'] if item['track']]
        all_track_uris.extend(uris)

# 7. Shuffle the mix so global and Bollywood songs are intermingled
random.shuffle(all_track_uris)
# Limit to 50 tracks total for a good playlist size
final_uris = all_track_uris[:50]

# 8. Create and Fill the Playlist
new_playlist = sp.user_playlist_create(
    user=user['id'], 
    name=f"My {mood.capitalize()} Global-Desi Mix", 
    public=True,
    description="Custom mix of global and Bollywood hits based on my mood."
)

sp.playlist_add_items(playlist_id=new_playlist['id'], items=final_uris)

print(f"\nSUCCESS! Created your {len(final_uris)}-track '{mood.capitalize()}' mix.")
print(f"Check your Spotify now!")