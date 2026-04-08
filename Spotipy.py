import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import streamlit as st
import plotly.express as px

# ========================
# 🎨 UI CONFIG (BASE)
# ========================
st.set_page_config(page_title="Spotify Insights Pro", layout="wide", page_icon="🎵")

# CSS Avanzado (Mantenido del código base para máxima estética)
st.markdown("""
<style>
    .stApp { background-color: #0b0b0f; color: #e5e5e5; }
    [data-testid="stDataFrame"] !important { background-color: #000000 !important; }
    button[data-baseweb="tab"] p { font-size: 24px !important; font-weight: bold !important; color: #c084fc !important; }
    [data-testid="stMetricLabel"] p { font-size: 28px !important; color: #ff4ecd !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] div { font-size: 20px !important; color: #ffffff !important; }
    h2 { font-size: 45px !important; color: #c084fc !important; text-shadow: 2px 2px #ff4ecd33; }
    .stDataFrame { background-color: #111116 !important; border: 1px solid #c084fc; border-radius: 10px; }
    section[data-testid="stSidebar"] { background-color: #0f0f14; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #c084fc; font-size: 60px; margin-bottom: 0px;'>
        🎧 SPOTIFY WRAPPED PRO
    </h1>
    <p style='text-align: center; color: #ff4ecd; font-size: 20px; letter-spacing: 2px;'>
        ANÁLISIS NEÓN & KPIs DE TU MÚSICA
    </p>
    <br>
""", unsafe_allow_html=True)

# ========================
# 🔐 AUTH
# ========================
auth_manager = SpotifyOAuth(
    client_id="ac4a4ecb20e34f0c8089010b345d2775",
    client_secret="245fe6358f7f4084ba1a3d8a7d46e172",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-library-read user-top-read",
    open_browser=True
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# ========================
# 📊 DATA PROCESSING (FUSIONADO)
# ========================
try:
    # Datos de Top (Código 1) y Biblioteca (Código 2)
    top_artists = sp.current_user_top_artists(limit=50, time_range='medium_term')
    top_tracks = sp.current_user_top_tracks(limit=50, time_range='medium_term')
    saved_tracks = sp.current_user_saved_tracks(limit=50)

    # DataFrames Artistas
    artists_list = [{"Artista": a["name"], "Imagen": a["images"][0]["url"] if a["images"] else ""} for a in top_artists["items"]]
    df_artists = pd.DataFrame(artists_list)

    # DataFrames Canciones (Fusionando campos de ambos códigos)
    tracks_list = [{
        "Cancion": t["name"],
        "Artista": t["artists"][0]["name"],
        "Album": t["album"]["name"],
        "Duracion_ms": t['duration_ms'],
        "Explicit": t['explicit'],
        "Fecha_Lanzamiento": t['album']['release_date'],
        "Imagen": t["album"]["images"][0]["url"] if t["album"]["images"] else ""
    } for t in top_tracks["items"]]
    df_tracks = pd.DataFrame(tracks_list)

    # Limpieza y Transformación
    df_tracks['Minutos'] = df_tracks['Duracion_ms'] / 60000
    df_tracks['Año'] = pd.to_datetime(df_tracks['Fecha_Lanzamiento'], errors='coerce').dt.year
    df_tracks['Año'] = df_tracks['Año'].fillna(0).astype(int)

    # ========================
    # ⚡ MÉTRICAS SUPERIORES (KPIs Mixtos)
    # ========================
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    with col1:
        st.metric(label="🎤 TOP ARTISTA", value=df_artists.iloc[0]["Artista"])
    with col2:
        st.metric(label="🎵 TOP CANCIÓN", value=df_tracks.iloc[0]["Cancion"])
    with col3:
        st.metric(label="🎧 TOTAL TRACKS", value=len(df_tracks))
    with col4:
        st.metric("⏳ TIEMPO TOTAL", f"{df_tracks['Minutos'].sum():.1f} min")
    with col5:
        unique_ratio = (df_tracks['Artista'].nunique() / len(df_tracks)) * 100
        st.metric("🧬 VARIEDAD", f"{unique_ratio:.1f}%")
    with col6:
        st.metric("🎵 CANCIONES ANALIZADAS", len(df_tracks))


    st.markdown("<hr style='border: 1px solid #c084fc;'>", unsafe_allow_html=True)

    # ========================
    # 📑 TABS (ESTILO NEÓN)
    # ========================
    tab1, tab2, tab3 = st.tabs(["ARTISTAS", "CANCIONES", "DEEP DIVE ANÁLISIS"])

    with tab1:
        st.subheader("Tus leyendas personales")
        
        # Gráfico de Pie de Artistas (Del código 2)
        art_counts = df_tracks['Artista'].value_counts().reset_index().head(10)
        art_counts.columns = ['Artista', 'Apariciones']
        
        c_pie1, c_pie2 = st.columns([1, 1])
        with c_pie1:
            # Lista de artistas con imagen (Del código 1)
            for i, row in df_artists.head(5).iterrows():
                c_img, c_txt = st.columns([1, 4])
                if row["Imagen"]: c_img.image(row["Imagen"], width=70)
                c_txt.markdown(f"<h3 style='color:#ff4ecd; margin-top:10px;'>{i+1}. {row['Artista']}</h3>", unsafe_allow_html=True)
        
        with c_pie2:
            fig_pie = px.pie(art_counts, values='Apariciones', names='Artista', hole=0.5,
                            color_discrete_sequence=px.colors.sequential.Purp)
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", legend_font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.subheader("Exploración del Dataset")
        st.dataframe(
            df_tracks[["Cancion", "Artista", "Album", "Año", "Explicit"]],
            use_container_width=True,
            hide_index=True
        )

        st.write("---")
        
        # Gráfico de Barras Neón (Del código 1)
        fig_bar = px.bar(
            art_counts, x="Artista", y="Apariciones",
            color="Apariciones",
            color_continuous_scale=["#c084fc", "#ff4ecd"],
            title="Concentración de Escucha por Artista"
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff", title_font_size=25,
            xaxis=dict(showgrid=False, color="#c084fc"),
            yaxis=dict(showgrid=True, gridcolor="#2a2a3a", color="#c084fc"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.subheader("🎯 Inteligencia de Datos y Toma de Decisiones")
        
        # --- KPI 1: COMPOSICIÓN DEL CATÁLOGO ---
        st.markdown("### 🏷️ KPI: Concentración de Álbumes por Artista")
        ana_col1, ana_col2 = st.columns([2, 1])
        
        with ana_col1:
            album_reach = df_tracks.groupby('Artista')['Album'].nunique().reset_index().sort_values(by='Album', ascending=False).head(10)
            album_reach.columns = ['Artista', 'Álbumes Distintos']
            fig_reach = px.bar(album_reach, x='Álbumes Distintos', y='Artista', orientation='h', 
                             color='Álbumes Distintos', color_continuous_scale='RdPu')
            fig_reach.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig_reach, use_container_width=True)
        
        with ana_col2:
            st.markdown(f"""
            <div style="background-color:#111116; padding:20px; border-radius:15px; border-left: 5px solid #ff4ecd;">
                <p style="color:#c084fc; font-weight:bold;">ESTRATEGIA RECOMENDADA</p>
                <p style="font-size:14px;">Si un artista tiene muchos álbumes únicos, tu perfil tiende a la exploración de discografías. Recomendación: Promocionar preventas de LP.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # --- KPI 2: ANÁLISIS TEMPORAL (Del código 2) ---
        st.markdown("### 📅 KPI: Tendencia de Lanzamientos (Nostalgia vs Novedad)")
        
        df_years = df_tracks[df_tracks['Año'] > 0]
        release_years = df_years['Año'].value_counts().reset_index().sort_values(by='Año')
        release_years.columns = ['Año', 'Cantidad']
        
        fig_trend = px.area(release_years, x='Año', y='Cantidad', 
                          color_discrete_sequence=['#ff4ecd'])
        fig_trend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_trend, use_container_width=True)
        
        st.info("**Decisión de Programación:** Si el gráfico muestra un pico en años anteriores a 2010, el algoritmo sugerirá playlists 'Throwback'.")

        # --- KPI 3: MÉTRICAS DE DIVERSIDAD (Cajas Estilizadas) ---
        st.markdown("### ⏱️ Resumen Ejecutivo de Perfil")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Explicit content", f"{(df_tracks['Explicit'].sum() / len(df_tracks)) * 100:.1f}%")
        with c2:
            st.metric("Duración Media", f"{df_tracks['Minutos'].mean():.2f} min")
        with c3:
            st.metric("Álbumes Únicos", df_tracks['Album'].nunique())
            
        st.warning("**Conclusión:** Usuario con alta duración media es ideal para anuncios de audio largos (Podcasts).")

except Exception as e:
    st.error(f"Error en la conexión. Revisa tus credenciales de Spotify. Detalle: {e}")