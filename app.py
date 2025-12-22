import streamlit as st
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

# Load secrets
load_dotenv()

# Streamlit UI Setup
st.set_page_config(page_title="Raag", page_icon="🎵")
st.title("🎵 Moodify: Global-Desi Mix")
st.markdown("Create a custom Spotify playlist based on your mood!")

# Spotify Auth
scope = "playlist-modify-public user-top-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope=scope
))

# User Interaction
mood = st.selectbox("How are you feeling?", ["Happy", "Sad", "Chill", "Workout"])

if st.button("Generate My Playlist"):
    with st.spinner("Mixing your tracks..."):
        user = sp.current_user()
        
        search_map = {
            "Happy":  ["happy upbeat pop 2025", "bollywood party hits"],
            "Sad":    ["sad melancholic acoustic", "hindi sad songs"],
            "Chill":  ["lofi chill study beats", "bollywood lofi"],
            "Workout": ["high energy gym phonk", "bollywood workout beats"]
        }
        
        queries = search_map.get(mood)
        all_track_uris = []
        
        for query in queries:
            search_results = sp.search(q=query, type='playlist', limit=1)
            playlist_id = search_results['playlists']['items'][0]['id']
            tracks = sp.playlist_items(playlist_id, limit=20)
            uris = [item['track']['uri'] for item in tracks['items'] if item['track']]
            all_track_uris.extend(uris)

        random.shuffle(all_track_uris)
        
        new_playlist = sp.user_playlist_create(
            user=user['id'], 
            name=f"My {mood} Global-Desi Mix", 
            description="Generated via Moodify Web App"
        )
        sp.playlist_add_items(playlist_id=new_playlist['id'], items=all_track_uris[:40])
        
        st.success(f"Done! Created your '{mood}' mix.")
        st.link_button("Open Playlist on Spotify", new_playlist['external_urls']['spotify'])