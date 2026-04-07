import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import streamlit as st
import plotly.express as px

# ========================
# 🎨 UI CONFIG
# ========================
st.set_page_config(page_title="Spotify Insights Pro", layout="wide", page_icon="🎵")

st.markdown("""
<style>
.stApp {
    background-color: #0b0b0f;
    color: white;
}

h1, h2, h3 {
    color: #c084fc !important;
}

p, div, span {
    color: #e5e5e5;
}

section[data-testid="stSidebar"] {
    background-color: #0f0f14;
}

input, textarea {
    background-color: #111116 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #c084fc;'>
        🎧 Spotify Wrapped Dashboard
    </h1>
    <p style='text-align: center; color: #ff4ecd;'>
        Tus canciones más escuchadas con estilo neón
    </p>
""", unsafe_allow_html=True)

# ========================
# 🔐 AUTH
# ========================
auth_manager = SpotifyOAuth(
    client_id="ac4a4ecb20e34f0c8089010b345d2775",
    client_secret="245fe6358f7f4084ba1a3d8a7d46e172",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-top-read",
    open_browser=True
)

sp = spotipy.Spotify(auth_manager=auth_manager)

# ========================
# 📊 DATA
# ========================
try:

    top_artists = sp.current_user_top_artists(limit=50, time_range='medium_term')
    top_tracks = sp.current_user_top_tracks(limit=50, time_range='medium_term')

    # ========================
    # ARTISTS
    # ========================
    artists = []

    for a in top_artists.get("items", []):
        artists.append({
            "Artista": a.get("name", "Unknown"),
            "Imagen": a.get("images", [{}])[0].get("url", "") if a.get("images") else ""
        })

    df_artists = pd.DataFrame(artists).dropna()

    # ========================
    # TRACKS
    # ========================
    tracks = []

    for t in top_tracks.get("items", []):
        tracks.append({
            "Cancion": t.get("name", "Unknown"),
            "Artista": t["artists"][0]["name"] if t.get("artists") else "Unknown",
            "Album": t.get("album", {}).get("name", "Unknown"),
            "Imagen": t.get("album", {}).get("images", [{}])[0].get("url", "") if t.get("album") else ""
        })

    df_tracks = pd.DataFrame(tracks).dropna()

    # ========================
    # METRICS
    # ========================
    c1, c2, c3 = st.columns(3)

    c1.metric("🎤 Top artista", df_artists.iloc[0]["Artista"])
    c2.metric("🎵 Top canción", df_tracks.iloc[0]["Cancion"])
    c3.metric("🎧 Canciones", len(df_tracks))

    st.write("---")

    # ========================
    # TABS
    # ========================
    tab1, tab2, tab3 = st.tabs(["🎤 Artistas", "🎵 Canciones", "📊 Análisis"])

    # ========================
    # 🎤 ARTISTS
    # ========================
    with tab1:

        st.subheader("🎤 Tus artistas más escuchados")

        # SOLO TOP ARTISTAS CON IMAGEN
        for i, row in df_artists.head(10).iterrows():

            col1, col2 = st.columns([1, 4])

            with col1:
                if row["Imagen"]:
                    st.image(row["Imagen"], width=100)

            with col2:
                st.markdown(f"""
                <div style="color:#ff4ecd; font-size:18px;">
                    <b>{row['Artista']}</b>
                </div>
                """, unsafe_allow_html=True)

    # ========================
    # 🎵 TRACKS
    # ========================
    with tab2:

        st.subheader("🎵 Tus canciones")

        st.dataframe(
            df_tracks[["Cancion", "Artista", "Album"]].style.set_properties(
                **{
                    "background-color": "#111116",
                    "color": "#ffffff",
                    "border-color": "#2a2a3a"
                }
            ),
            use_container_width=True
        )

        st.subheader("🖼️ Portadas")

        for _, row in df_tracks.head(10).iterrows():

            col1, col2 = st.columns([1, 4])

            with col1:
                if row["Imagen"]:
                    st.image(row["Imagen"], width=100)

            with col2:
                st.markdown(f"""
                <div style="color:#ff4ecd; font-size:18px;"><b>{row['Cancion']}</b></div>
                <div style="color:#c084fc;">🎤 {row['Artista']}</div>
                <div style="color:#aaa;">💿 {row['Album']}</div>
                """, unsafe_allow_html=True)

        # gráfico
        artist_count = df_tracks["Artista"].value_counts().reset_index()
        artist_count.columns = ["Artista", "Repeticiones"]

        fig = px.bar(
            artist_count.head(15),
            x="Artista",
            y="Repeticiones",
            title="🎤 Artistas más escuchados"
        )

        fig.update_layout(
            paper_bgcolor="#0b0b0f",
            plot_bgcolor="#0b0b0f",
            font_color="#ff4ecd"
        )

        st.plotly_chart(fig, use_container_width=True)

    # ========================
    # 📊 ANALYSIS
    # ========================
    with tab3:

        st.subheader("📊 Insights")

        artist_count = df_tracks["Artista"].value_counts().reset_index()
        artist_count.columns = ["Artista", "Repeticiones"]

        st.write("🔥 Artista top:", artist_count.iloc[0]["Artista"])
        st.write("🎧 Canción top:", df_tracks["Cancion"].value_counts().idxmax())
        st.write("💿 Álbum top:", df_tracks["Album"].value_counts().idxmax())

except Exception as e:
    st.error(f"Error: {e}")