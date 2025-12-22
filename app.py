import plotly.express as px
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

        # Track mood counts in the session
if 'mood_counts' not in st.secrets: # In a real app, use a DB. For now, we simulate:
    st.session_state.mood_counts = {"Happy": 15, "Sad": 10, "Energetic": 25, "Calm": 8}

with st.sidebar:
    st.header("📊 Trending Moods")
    
    # Your mood data
    mood_data = {"Mood": ["Happy", "Sad", "Energetic", "Calm"], 
                 "Count": [15, 10, 25, 8]}
    
    # Create a colorful Plotly bar chart
    fig = px.bar(mood_data, x='Mood', y='Count', 
                 color='Mood', # This makes each bar a different color
                 color_discrete_map={
                     "Happy": "#FFD700",    # Gold
                     "Sad": "#4682B4",      # Steel Blue
                     "Energetic": "#FF4500", # Orange Red
                     "Calm": "#3CB371"       # Medium Sea Green
                 },
                 template="plotly_dark") # Matches Spotify's dark theme
    
    # Remove unnecessary labels for a cleaner sidebar look
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
    
    st.plotly_chart(fig, use_container_width=True)

    from PIL import Image, ImageDraw, ImageFont
import io

def generate_cover(mood_name):
    # Create a square canvas with a gradient or solid color
    img = Image.new('RGB', (640, 640), color = (30, 215, 96)) # Spotify Green
    d = ImageDraw.Draw(img)
    
    # Add text (You can customize fonts later)
    d.text((100, 280), f"My {mood_name} Raag", fill=(255, 255, 255))
    
    # Save to a byte buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

# Inside your "Generate" button logic:
cover_image = generate_cover(mood)
st.download_button(
    label="🖼️ Download Playlist Cover",
    data=cover_image,
    file_name=f"{mood}_cover.png",
    mime="image/png"
)