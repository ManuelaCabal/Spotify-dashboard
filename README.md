🎵 Spotify Insights Pro
Dashboard interactivo de analítica avanzada para usuarios de Spotify, construido con Streamlit, que permite explorar en profundidad hábitos musicales, tendencias y métricas clave a partir de tu actividad en la plataforma.
🚀 Descripción
Spotify Insights Pro es una aplicación que replica y amplía el concepto de Spotify Wrapped, ofreciendo:
Análisis de artistas y canciones más escuchadas
KPIs personalizados sobre tu consumo musical
Visualizaciones interactivas
Perfil psico-acústico basado en datos reales
Todo presentado en una interfaz moderna, oscura y altamente visual.
🧠 Funcionalidades:
📊 Métricas principales
🎤 Top artista
🎵 Top canción
🎼 Álbum más frecuente
⏳ Tiempo total de escucha
🧬 Nivel de diversidad musical
💽 Número de canciones analizadas
🎧 Análisis de artistas
Ranking visual de los artistas más escuchados
Gráfico de distribución de escucha (pie chart)
Indicadores de concentración musical
Insights automáticos sobre fidelidad musical
🎼 Exploración de canciones
Dataset interactivo con:
Canción
Artista
Álbum
Año
Contenido explícito
Gráfico de barras de concentración por artista
📈 Análisis avanzado
Distribución de álbumes por artista
Tendencias temporales (nostalgia vs actualidad)
KPIs de comportamiento:
Duración media
Diversidad de artistas
Rango temporal
Contenido explícito
🛠️ Tecnologías utilizadas
Python
Streamlit → interfaz web interactiva
Spotipy → conexión con API de Spotify
Pandas → procesamiento de datos
Plotly → visualizaciones dinámicas
🔐 Autenticación
La app utiliza OAuth 2.0 de Spotify para acceder a los datos del usuario.
Scopes utilizados:
user-library-read
user-top-read
⚙️ Instalación
Clona este repositorio:
git clone https://github.com/tuusuario/spotify-insights-pro.git
cd spotify-insights-pro
Instala las dependencias:
pip install -r requirements.txt
Configura tus credenciales de Spotify:
Crea una app en:
👉 https://developer.spotify.com/dashboard/
Y reemplaza en el código:
client_id="TU_CLIENT_ID"
client_secret="TU_CLIENT_SECRET"
redirect_uri="http://127.0.0.1:8888/callback"
▶️ Uso
Ejecuta la app con:
streamlit run app.py
Se abrirá automáticamente en tu navegador para autenticarte con Spotify.
🎨 UI / Diseño
Tema oscuro personalizado
Tipografía y métricas centradas
Estética tipo dashboard profesional
Gráficos estilo “neón” con Plotly
📊 Insights generados
El sistema genera conclusiones automáticas como:
Nivel de fidelidad a artistas
Perfil de exploración musical
Tendencias generacionales
Recomendaciones estratégicas de consumo
