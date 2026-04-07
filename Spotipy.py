import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Spotify Insights Pro", layout="wide")
st.title("📊 Mi Análisis Personal de Spotify")

# CONFIGURACIÓN
auth_manager = SpotifyOAuth(
    client_id="ac4a4ecb20e34f0c8089010b345d2775",
    client_secret="245fe6358f7f4084ba1a3d8a7d46e172",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-top-read user-library-read playlist-read-private",
    open_browser=True 
)

sp = spotipy.Spotify(auth_manager=auth_manager)

try:
    # 1. OBTENER DATOS
    top_artists_res = sp.current_user_top_artists(limit=20, time_range='medium_term')
    top_tracks_res = sp.current_user_top_tracks(limit=20, time_range='medium_term')

    # --- PROCESAMIENTO DE ARTISTAS (CORREGIDO) ---
    artists_data = []
    for art in top_artists_res.get('items', []):
        # Usamos .get() y validamos que 'genres' sea una lista con contenido
        generos_lista = art.get('genres', [])
        generos_str = ", ".join(generos_lista[:2]) if generos_lista else "Sin género"
        
        artists_data.append({
            'Artista': art.get('name', 'Desconocido'),
            'Géneros': generos_str,
            'Seguidores': art.get('followers', {}).get('total', 0),
            'Popularidad': art.get('popularity', 0)
        })
    df_artists = pd.DataFrame(artists_data)

    # --- PROCESAMIENTO DE CANCIONES (CORREGIDO) ---
    tracks_data = []
    for track in top_tracks_res.get('items', []):
        tracks_data.append({
            'Canción': track.get('name', 'Desconocida'),
            'Artista': track['artists'][0]['name'] if track.get('artists') else "Desconocido",
            'Álbum': track.get('album', {}).get('name', 'N/A'),
            'Popularidad': track.get('popularity', 0)
        })
    df_tracks = pd.DataFrame(tracks_data)

    # --- INTERFAZ ---
    if not df_artists.empty and not df_tracks.empty:
        tab1, tab2, tab3 = st.tabs(["🔝 Top Artistas", "🎵 Top Canciones", "📈 Análisis"])

        with tab1:
            st.subheader("Tus 20 Artistas más escuchados")
            st.dataframe(df_artists, use_container_width=True)
            
        with tab2:
            st.subheader("Tus 20 Canciones preferidas")
            st.dataframe(df_tracks, use_container_width=True)

        with tab3:
            st.subheader("Comparativa de Popularidad")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Popularidad por Artista**")
                st.bar_chart(df_artists.set_index('Artista')['Popularidad'])
            with col2:
                st.write("**Popularidad por Canción**")
                st.line_chart(df_tracks.set_index('Canción')['Popularidad'])

        # MÉTRICAS RÁPIDAS
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Artista Top", df_artists['Artista'].iloc[0])
        c2.metric("Canción Top", df_tracks['Canción'].iloc[0])
        c3.metric("Popularidad Media", round(df_tracks['Popularidad'].mean(), 1))
    else:
        st.warning("No se encontraron suficientes datos en tu historial reciente.")

except Exception as e:
    st.error(f"Error detectado: {e}")
    st.info("💡 Si el error persiste: Borra el archivo .cache de la carpeta y reinicia la App.")