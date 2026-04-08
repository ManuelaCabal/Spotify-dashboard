import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import streamlit as st
import plotly.express as px

# 🎨 UI CONFIG (BASE)
st.set_page_config(page_title="Spotify Insights Pro", layout="wide", page_icon="🎵")

# CSS Avanzado 
st.markdown("""
<style>
    .stApp { background-color: #0b0b0f; color: #e5e5e5; }
    [data-testid="stDataFrame"] !important { background-color: #000000 !important; }
    /* Cambiar color de los captions (las explicaciones debajo de las métricas) */
    [data-testid="stCaptionContainer"] {
        color: #ffffff !important;
        font-size: 20px !important;
        opacity: 0.9;
        font-weight: 500;
        text-align: center;
    }
    button[data-baseweb="tab"] p { font-size: 24px !important; font-weight: bold !important; color: #c084fc !important; }
    [data-testid="stMetricLabel"] p { font-size: 28px !important; color: #ff4ecd !important; font-weight: bold !important; }
    [data-testid="stMetricValue"] div { font-size: 20px !important; color: #ffffff !important; text-align: center !important; }
    h2 { font-size: 45px !important; color: #c084fc !important; text-shadow: 2px 2px #ff4ecd33; }
    .stDataFrame { background-color: #111116 !important; border: 1px solid #c084fc; border-radius: 10px; }
    section[data-testid="stSidebar"] { background-color: #0f0f14; }
    /* Centrar todo el contenedor de la métrica */
    [data-testid="stMetric"] {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-shadow: 2px 2px #ff4ecd33;
    }

    /* Centrar específicamente la etiqueta (label/título) */
    [data-testid="stMetricLabel"] {
        display: justify-content;
        justify-content: center;
        width: 100%;
    }

    /* Centrar el valor numérico o texto principal */
    [data-testid="stMetricValue"] {
        display: justify-content;
        justify-content: center;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #c084fc; font-size: 60px;text-shadow: 2px 2px #ff4ecd33; margin-bottom: 0px;'>
        SPOTIFY WRAPPED
    </h1>
    <p style='text-align: center; color: #ffffff; font-size: 20px; letter-spacing: 2px;'>
        Dashboard de analítica avanzada para usuarios de Spotify. Explora KPIs detallados sobre la composición de tu biblioteca, tendencias temporales y perfiles psico-acústicos. Una inmersión profunda en tu ecosistema digital diseñada para la toma de decisiones basada en datos musicales.
    </p>
    <br>
""", unsafe_allow_html=True)

# AUTH
auth_manager = SpotifyOAuth(
    client_id="ac4a4ecb20e34f0c8089010b345d2775",
    client_secret="245fe6358f7f4084ba1a3d8a7d46e172",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-library-read user-top-read",
    open_browser=True
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# DATA PROCESSING 
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

    # MÉTRICAS SUPERIORES 
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    with col1:
        st.metric(label="🎤 TOP ARTISTA 🎤", value=df_artists.iloc[0]["Artista"])
    with col2:
        st.metric(label="🎵 TOP CANCIÓN 🎵", value=df_tracks.iloc[0]["Cancion"])
    with col3:
        top_album_val = df_tracks['Album'].mode()[0] if not df_tracks.empty else "N/A"
        st.metric(label="🎼 TOP ALBUM 🎼", value=top_album_val)
    with col4:
        st.metric("⏳ TIEMPO TOTAL ⏳", f"{df_tracks['Minutos'].sum():.1f} min")
    with col5:
        unique_ratio = (df_tracks['Artista'].nunique() / len(df_tracks)) * 100
        st.metric("🧬 VARIEDAD 🧬", f"{unique_ratio:.1f}%")
    with col6:
        st.metric("💽 CANCIONES ANALIZADAS 💽 ", len(df_tracks))


    st.markdown("<hr style='border: 1px solid #c084fc;'>", unsafe_allow_html=True)
    # TABS 
    tab1, tab2, tab3 = st.tabs(["ARTISTAS", "CANCIONES", "ANÁLISIS"])

    with tab1:
        st.markdown("<h2 style='text-align: center;'>Análisis de Fidelidad Musical</h2>", unsafe_allow_html=True)
        
        # 1. PREPARACIÓN DE DATOS
        art_counts = df_tracks['Artista'].value_counts().reset_index().head(10)
        art_counts.columns = ['Artista', 'Apariciones']

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. DISEÑO DE COLUMNAS
        c_lista, c_grafica = st.columns([1, 1], gap="large")

        with c_lista:
            st.markdown("#### 🏆 Top 10 artistas más escuchados")
            for i, row in df_artists.head(10).iterrows():
                row_cols = st.columns([1, 4])
                if row["Imagen"]:
                    row_cols[0].markdown(f"""
                        <img src="{row['Imagen']}" 
                             style="border-radius: 50%; width: 80px; height: 80px; 
                                    object-fit: cover; border: 2px solid #c084fc;">
                    """, unsafe_allow_html=True)
                row_cols[1].markdown(f"<p style='color:#ff4ecd; font-size:25px; margin-top:25px;'>{i+1}. <b>{row['Artista']}</b></p>", unsafe_allow_html=True)

        with c_grafica:
            st.markdown("#### 📊 Distribución de Cuota")
            fig_pie = px.pie(
                art_counts, 
                values='Apariciones', 
                names='Artista', 
                hole=0.6,
                color_discrete_sequence=px.colors.sequential.Purp
            )
            
            # --- CONFIGURACIÓN PARA MOSTRAR NOMBRES Y % ---
            fig_pie.update_traces(
                textposition='inside',      
                textinfo='label+percent',  
                insidetextorientation='horizontal', 
                textfont_size=14,
                marker=dict(line=dict(color='#0b0b0f', width=2))
            )

            fig_pie.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=False 
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            # --- INFORMACIÓN DE CONTEXTO JUSTO DEBAJO ---
            top_1_name = art_counts['Artista'].iloc[0]
            total_top_10 = art_counts['Apariciones'].sum()
            concentracion = (art_counts['Apariciones'].iloc[0] / total_top_10) * 100
            
            inf_col1, inf_col2 = st.columns(2)
            with inf_col1:
                st.markdown(f"""
                    <div style='text-align:center;'>
                        <p style='color:#c084fc; font-weight:bold; margin-bottom:0; font-size:20px;'>LÍDER</p>
                        <p style='font-size:20px;'>{top_1_name}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='text-align:center;'>
                        <p style='color:#c084fc; font-weight:bold; margin-bottom:0;font-size:20px;'>CUOTA TOP 1</p>
                        <p style='font-size:20px;'>{concentracion:.1f}%</p>
                    </div>
                """, unsafe_allow_html=True)
            with inf_col2:
                st.markdown(f"""
                    <div style='text-align:center;'>
                        <p style='color:#c084fc; font-weight:bold; margin-bottom:0;font-size:20px;'>VOLUMEN</p>
                        <p style='font-size:20px;'>{total_top_10} Tracks</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='text-align:center;'>
                        <p style='color:#c084fc; font-weight:bold; margin-bottom:0;font-size:20px;'>DIVERSIDAD</p>
                        <p style='font-size:20px;'>{'Alta' if concentracion < 20 else 'Baja'}</p>
                    </div>
                """, unsafe_allow_html=True)

            # Cuadro de conclusión
            st.markdown(f"""
    <div style="background-color:#111116; padding:20px; border-radius:15px; border-left: 5px solid #ff4ecd; box-shadow: 0px 0px 10px rgba(192, 132, 252, 0.1);">
        <p style="color:#c084fc; font-weight:bold; font-size:22px; margin-bottom:10px;">📊 ANÁLISIS DE CONCENTRACIÓN</p>
        <p style="color:#ffffff; font-size:18px; line-height:1.4;">
            Tu consumo está altamente concentrado en <b style="color:#ff4ecd;">{top_1_name}</b>, 
            quien define el <b style="color:#c084fc;">{concentracion:.1f}%</b> de tu tendencia actual.
            <br><br>
            <span style="color:#c084fc; font-weight:bold;">Insight:</span> Presentas un perfil de oyente con alta lealtad de marca hacia un artista principal.
        </p>
    </div>
""", unsafe_allow_html=True)
    with tab2:
        st.subheader("Exploración del Dataset")
        
        # Usamos un contenedor para aplicar el estilo visual
        st.markdown('<div class="dark-table">', unsafe_allow_html=True)
        st.dataframe(
            df_tracks[["Cancion", "Artista", "Album", "Año", "Explicit"]],
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        
        # Gráfico de Barras Neón 
        fig_bar = px.bar(
            art_counts, x="Artista", y="Apariciones",
            color="Apariciones",
            color_continuous_scale=["#c084fc", "#ff4ecd"],
            title="Concentración de Escucha por Artista"
        )
        
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            title_font_color="#c084fc", 
            font_color="#FFFFFF", 
            title_font_size=40,
            xaxis=dict(showgrid=False, color="#c084fc"),
            yaxis=dict(showgrid=True, gridcolor="#fdfdfd", color="#c084fc"),
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown(f"""
    <div style="background-color:#111116; padding:20px; border-radius:15px; border-left: 5px solid #ff4ecd; box-shadow: 0px 0px 10px rgba(192, 132, 252, 0.1);">
        <p style="color:#c084fc; font-weight:bold; font-size:22px; margin-bottom:10px;">📉 CONCLUSIÓN DEL CONSUMO</p>
        <p style="color:#ffffff; font-size:18px; line-height:1.4;">
            Tu ecosistema musical está liderado por <b style="color:#ff4ecd;">Eslabon Armado</b>, seguido de cerca por <b style="color:#ff4ecd;">Luigi 21 Plus</b>, mostrando una clara preferencia por los géneros regionales y urbanos. 
            <br><br>
            A pesar del dominio del Top 1, tienes una <span style="color:#c084fc; font-weight:bold;">base diversificada</span> con artistas como Pimpinela y Mon Laferte, lo que equilibra tu perfil entre éxitos actuales y clásicos sentimentales.
        </p>
    </div>
""", unsafe_allow_html=True)

    with tab3:        
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
            <div style="background-color:#111116; padding:20px; border-radius:15px; border-left: 5px solid #ff4ecd; box-shadow: 0px 0px 10px rgba(192, 132, 252, 0.1);">
                <p style="color:#c084fc; font-weight:bold; font-size:22px; margin-bottom:10px;">🎯 ESTRATEGIA COMERCIAL</p>
                <p style="color:#ffffff; font-size:18px; line-height:1.4;">
                    Si un artista presenta múltiples <b style="color:#ff4ecd;">álbumes únicos</b>, tu perfil indica una tendencia a la exploración profunda de discografías. 
                    <br><br>
                    <span style="color:#c084fc; font-weight:bold;">Recomendación:</span> Priorizar campañas de fidelización y <b style="color:#ff4ecd;">preventas de LP</b> o ediciones especiales.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # --- KPI 2: ANÁLISIS TEMPORAL (Del código 2) ---
        st.markdown("### 📅 KPI: Tendencia de Lanzamientos Nostalgia vs Novedad")
        
        df_years = df_tracks[df_tracks['Año'] > 0]
        release_years = df_years['Año'].value_counts().reset_index().sort_values(by='Año')
        release_years.columns = ['Año', 'Cantidad']
        
        fig_trend = px.area(release_years, x='Año', y='Cantidad', 
                          color_discrete_sequence=['#ff4ecd'])
        fig_trend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        fig_trend.update_traces(fill='toself', line_color='#ff4ecd', fillcolor='rgba(255, 78, 205, 0.2)')
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown(f"""
            <div style="background-color:#111116; padding:20px; border-radius:15px; border-left: 5px solid #ff4ecd; box-shadow: 0px 0px 10px rgba(255, 78, 205, 0.1);">
                <p style="color:#c084fc; font-weight:bold; font-size:20px; margin-bottom:10px;">🚀 DECISIÓN DE PROGRAMACIÓN</p>
                <p style="color:#ffffff; font-size:18px; line-height:1.4;">
                    Si el gráfico muestra un pico en años anteriores a <b style="color:#ff4ecd;">2010</b>, 
                    el algoritmo de curaduría sugerirá automáticamente playlists de tipo <b style="color:#ff4ecd;">'Throwback'</b> para maximizar el engagement.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # --- KPI 3: MÉTRICAS DE DIVERSIDAD (Cajas Estilizadas) ---
        st.markdown("---")
        st.markdown("### ⏱️ Resumen Ejecutivo de Perfil")
        
        c1, c2, c3 = st.columns(3)
        c4, c5, c6 = st.columns(3) 

        with c1:
            st.metric("Contenido Explícito", f"{(df_tracks['Explicit'].sum() / len(df_tracks)) * 100:.1f}%")
            st.caption("Refleja el porcentaje de lírica con lenguaje explícito en tu catálogo.")
            
        with c2:
            st.metric("Duración Media", f"{df_tracks['Minutos'].mean():.2f} min")
            st.caption("Promedio de tiempo por track. Define tu preferencia de formato.")
            
        with c3:
            st.metric("Álbumes Únicos", df_tracks['Album'].nunique())
            st.caption("Indica la diversidad de producciones completas exploradas.")

        with c4:
            st.metric("Artistas Únicos", df_tracks['Artista'].nunique())
            st.caption("Mide el grado de dispersión o concentración de tu biblioteca.")
            
        with c5:
            st.metric("Duración Total", f"{df_tracks['Minutos'].sum():.1f} min")
            st.caption("Volumen total de tiempo analizado en este dataset.")
            
        with c6:
            st.metric("Años Representados", df_tracks['Año'].nunique())
            st.caption("Mide la amplitud generacional y el rango temporal de tu gusto.")

        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="background-color:#111116; padding:20px; border-radius:15px; border-left: 5px solid #ff4ecd; box-shadow: 0px 0px 10px rgba(255, 78, 205, 0.2);">
                <p style="color:#ffffff; font-weight:bold; font-size:20px; margin-bottom:10px;">📊 CONCLUSIÓN ESTRATÉGICA</p>
                <p style="color:#ffffff; font-size:18px; line-height:1.4;">
                    El análisis de los <b style="color:#c084fc;">{df_tracks['Año'].nunique()}</b> años representados y tu duración media de <b style="color:#c084fc;">{df_tracks['Minutos'].mean():.2f} min</b> 
                    sugiere un perfil de usuario con alta retención de atención, ideal para la inserción de formatos largos como Podcasts o Audiobooks.
                </p>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error en la conexión. Revisa tus credenciales de Spotify. Detalle: {e}")