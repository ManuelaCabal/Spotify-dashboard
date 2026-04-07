import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Spotify Final", layout="wide")
st.title("💗 Mi Spotify Dashboard")

# CONFIGURACIÓN DIRECTA
auth_manager = SpotifyOAuth(
    client_id="ac4a4ecb20e34f0c8089010b345d2775",
    client_secret="245fe6358f7f4084ba1a3d8a7d46e172",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="playlist-read-private",
    open_browser=True # Esto abrirá la pestaña automáticamente
)

sp = spotipy.Spotify(auth_manager=auth_manager)

try:
    # Intentar cargar datos del Top 50 Global (ID fijo)
    st.info("🔄 Conectando con Spotify... Si se queda cargando, mira la terminal.")
    results = sp.playlist_tracks("3PjmozMCNtqqNAGr27TjZc")


    tracks = []
    for item in results['items']:
        # En tu JSON, el track está dentro de item['item']
        # Usamos .get() por seguridad
        inner_item = item.get('item') 
        
        if inner_item:
            # Aquí extraemos los datos del track real
            name = inner_item.get('name')
            artist = inner_item['artists'][0]['name'] if inner_item.get('artists') else "Desconocido"
            
            # OJO: El campo 'popularity' NO siempre viene en la respuesta de playlist_tracks
            # Si sale error, usa .get('popularity', 0)
            popularity = inner_item.get('popularity', 0) 

            tracks.append({
                'Canción': name,
                'Artista': artist,
                'Popularidad': popularity
            })
            
    df = pd.DataFrame(tracks)

    if not df.empty:
        st.success("✅ ¡CONECTADO!")
        st.dataframe(df) # Muestra la tabla
        st.bar_chart(df.set_index('Canción')['Popularidad']) # Muestra el gráfico
    else:
        st.error("No se recibieron datos.")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("PASO DE RESCATE: 1. Borra el archivo .cache en tu carpeta. 2. Reinicia la terminal.")