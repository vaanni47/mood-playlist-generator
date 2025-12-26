import streamlit.components.v1 as components
import plotly.express as px
import streamlit as st
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
from PIL import Image, ImageDraw
import io
from streamlit_lottie import st_lottie
import requests

# 1. SETUP & AUTH
load_dotenv()

st.set_page_config(page_title="Raag", page_icon="🎵", layout="wide")

# Helper for Lottie
# Updated robust Lottie URL
lottie_url = "https://lottie.host/819d268a-215f-4d92-951b-741a34a1795b/In107f9J9P.json"

def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_music = load_lottieurl(lottie_url)

with st.sidebar:
    if lottie_music:
        st_lottie(lottie_music, height=150, key="music_visualizer")
    else:
        st.markdown("🎵 **Raag Music Mode**")

# Spotify Auth
scope = "playlist-modify-public user-top-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope=scope,
    show_dialog=True
))

# 2. SESSION STATE INITIALIZATION
if 'mood_counts' not in st.session_state:
    st.session_state.mood_counts = {"Happy": 15, "Sad": 10, "Chill": 25, "Workout": 8}

if 'history' not in st.session_state:
    st.session_state.history = []

# 3. HELPER FUNCTIONS
def generate_cover(mood_name):
    img = Image.new('RGB', (640, 640), color=(30, 215, 96)) # Spotify Green
    d = ImageDraw.Draw(img)
    d.text((150, 300), f"RAAG: {mood_name.upper()}", fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# 4. SIDEBAR
with st.sidebar:
    # Only show if the animation loaded successfully
    if lottie_music:
        st_lottie(lottie_music, height=150, key="music_visualizer")
    else:
        st.write("🎵") # Fallback icon if animation fails
    
    st.header("📊 Trending Moods")
    # ... rest of your sidebar code ...
    mood_data = {
        "Mood": list(st.session_state.mood_counts.keys()), 
        "Count": list(st.session_state.mood_counts.values())
    }
    fig = px.bar(mood_data, x='Mood', y='Count', color='Mood',
                 color_discrete_map={"Happy": "#FFD700", "Sad": "#4682B4", "Chill": "#3CB371", "Workout": "#FF4500"},
                 template="plotly_dark")
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0), height=300)
    st.plotly_chart(fig, use_container_width=True)

# 5. MAIN INTERFACE
mood = st.selectbox("How are you feeling?", ["Happy", "Sad", "Chill", "Workout"])

if st.button("Generate My Playlist"):
    with st.spinner("Mixing your tracks..."):
        # Update session state for trending chart
        st.session_state.mood_counts[mood] += 1
        
        user = sp.current_user()
        search_map = {
            "Happy":   ["happy upbeat pop 2025", "bollywood party hits"],
            "Sad":     ["sad melancholic acoustic", "hindi sad songs"],
            "Chill":   ["lofi chill study beats", "bollywood lofi"],
            "Workout": ["high energy gym phonk", "bollywood workout beats"]
        }
        
        queries = search_map.get(mood)
        all_track_uris = []
        
        for query in queries:
            search_results = sp.search(q=query, type='playlist', limit=1)
            if search_results['playlists']['items']:
                p_id = search_results['playlists']['items'][0]['id']
                tracks = sp.playlist_items(p_id, limit=20)
                uris = [item['track']['uri'] for item in tracks['items'] if item['track']]
                all_track_uris.extend(uris)

        random.shuffle(all_track_uris)
        
        # Create Playlist
        new_playlist = sp.user_playlist_create(
            user=user['id'], 
            name=f"My {mood} Global-Desi Mix", 
            description="Generated via Moodify Web App",
            public=True
        )
        sp.playlist_add_items(playlist_id=new_playlist['id'], items=all_track_uris[:40])
        
        playlist_url = new_playlist['external_urls']['spotify']
        playlist_id = new_playlist['id']

        # ADD TO HISTORY
        st.session_state.history.append({
            "mood": mood,
            "url": playlist_url,
            "id": playlist_id
        })

        st.success(f"Done! Created your '{mood}' mix.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("🚀 Open on Spotify", playlist_url)
        with col2:
            cover_image = generate_cover(mood)
            st.download_button(
                label="🖼️ Download Cover",
                data=cover_image,
                file_name=f"{mood}_cover.png",
                mime="image/png"
            )

        st.markdown("---")
        st.markdown("### 🎧 Preview your Raag Mix")
        embed_link = f"https://open.spotify.com/embed/playlist/{playlist_id}?utm_source=generator&theme=0"
        components.iframe(embed_link, height=380, scrolling=False)

# 6. DISPLAY HISTORY (Outside the button, so it stays visible)
if st.session_state.history:
    st.markdown("---")
    st.markdown("## 🕒 Recent Raags")
    # Show last 4 entries
    recent_items = st.session_state.history[-4:]
    cols = st.columns(len(recent_items)) 
    
    for i, item in enumerate(recent_items):
        with cols[i]:
            st.info(f"🎭 {item['mood']}")
            st.link_button("View Mix", item['url'], key=f"hist_{i}")