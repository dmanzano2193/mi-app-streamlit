import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image
import numpy as np
import re
import string

# Lista de stopwords en español adicionales
stopwords = set(STOPWORDS)
additional_stopwords = {
    "un", "una", "es", "y", "a", "el", "la", "que", "de", "en", "lo", "los", "las",
    "para", "con", "no", "del", "al", "se", "por", "como", "más", "o", "sus", "pero",
    "si", "le", "ya", "o", "ha", "me", "sin", "esto", "su", "yo", "bien", "aquí", "ha", "son",
    "sí", "ni", "e", "fuera", "porque", "cada", "ese", "tan", "todo", "todos", "nos", "nosotros",
    "usted", "ustedes", "él", "tu", "te","ella", "ellas", "ellos", "uno", "una", "mis", "mi", "nuestra", "nuestro"
}
stopwords = stopwords.union(additional_stopwords)

# Función para limpiar el texto
def clean_text(text):
    text = text.lower()  # Convertir a minúsculas
    text = re.sub(f"[{string.punctuation}]", " ", text)  # Remover puntuación
    text = re.sub("\s+", " ", text)  # Remover espacios extra
    words = text.split()
    return " ".join(word for word in words if word not in stopwords)

# Cargar los datos
df = pd.read_csv('pollo_campero_ejemplo_final.csv')

# Convertir columna 'date' a formato datetime
df['date'] = pd.to_datetime(df['date'])

# Configuración de la página
st.set_page_config(page_title="Pollo Campero Dashboard", layout="wide")

# Título del Dashboard con el logo
st.image("logo_pollo_campero.jpg", width=300)
st.title("Pollo Campero Instagram Dashboard")

# Selector de rango de fechas
st.header("Seleccione el rango de fechas")
start_date = st.date_input("Fecha de inicio", value=df['date'].min())
end_date = st.date_input("Fecha de fin", value=df['date'].max())

# Filtrar los datos por el rango de fechas seleccionado
df_filtered = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

# Métricas Generales
st.header("Métricas Generales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Publicaciones", f"{len(df_filtered):,}")
col2.metric("Total de Likes", f"{int(df_filtered['likes'].sum()):,}")
col3.metric("Total de Comentarios", f"{int(df_filtered['comments'].sum()):,}")
col4.metric("Total de Vistas de Video", f"{int(df_filtered['video_view_count'].sum()):,}")

# Posts con más likes y comentarios
st.header("Top Publicaciones")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 5 Publicaciones con más Likes")
    top_likes = df_filtered.nlargest(5, 'likes')
    st.dataframe(top_likes[['caption', 'likes', 'comments', 'video_view_count', 'url']])

with col2:
    st.subheader("Top 5 Publicaciones con más Comentarios")
    top_comments = df_filtered.nlargest(5, 'comments')
    st.dataframe(top_comments[['caption', 'likes', 'comments', 'video_view_count', 'url']])

# Gráficos de Análisis
st.header("Gráficos de Análisis")

# Colocar los gráficos en dos columnas
col1, col2 = st.columns(2)

# Likes y Comentarios a lo largo del tiempo
with col1:
    st.subheader("Likes y Comentarios a lo largo del tiempo")
    likes_comments_fig = px.line(df_filtered, x='date', y=['likes', 'comments'], labels={'value': 'Cantidad', 'date': 'Fecha'})
    likes_comments_fig.update_layout(title='Likes y Comentarios a lo largo del tiempo', height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(likes_comments_fig, use_container_width=True)

# Distribución de Likes
with col2:
    st.subheader("Distribución de Likes")
    likes_hist_fig = px.histogram(df_filtered, x='likes', nbins=30, title='Distribución de Likes')
    likes_hist_fig.update_xaxes(title='Likes')
    likes_hist_fig.update_yaxes(title='Frecuencia')
    likes_hist_fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(likes_hist_fig, use_container_width=True)

# Distribución de Comentarios
with col1:
    st.subheader("Distribución de Comentarios")
    comments_hist_fig = px.histogram(df_filtered, x='comments', nbins=30, title='Distribución de Comentarios')
    comments_hist_fig.update_xaxes(title='Comentarios')
    comments_hist_fig.update_yaxes(title='Frecuencia')
    comments_hist_fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(comments_hist_fig, use_container_width=True)

# Vistas de Video a lo largo del tiempo
with col2:
    st.subheader("Vistas de Video a lo largo del tiempo")
    video_views_fig = px.line(df_filtered[df_filtered['is_video'] == True], x='date', y='video_view_count', labels={'video_view_count': 'Reproducciones de Video', 'date': 'Fecha'})
    video_views_fig.update_layout(title='Vistas de Video a lo largo del tiempo', height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(video_views_fig, use_container_width=True)

# Top 5 Publicaciones con más Vistas de Video
st.subheader("Top 5 Publicaciones con más Vistas de Video")
top_video_views = df_filtered[df_filtered['is_video'] == True].nlargest(5, 'video_view_count')
video_views_fig_bar = px.bar(top_video_views, x='caption', y='video_view_count', title='Top 5 Videos con más Vistas',
                             labels={'caption': 'Caption', 'video_view_count': 'Reproducciones de Video'})
video_views_fig_bar.update_layout(xaxis_tickangle=-90, xaxis_showticklabels=False, height=400, margin=dict(l=0, r=0, t=40, b=0))
st.plotly_chart(video_views_fig_bar, use_container_width=True)

# Análisis de Hashtags
st.header("Análisis de Hashtags")
col1, col2 = st.columns(2)

with col1:
    hashtags_series = df_filtered['hashtags'].explode()
    hashtags_series = hashtags_series[hashtags_series.notna()]  # Eliminar hashtags vacíos
    hashtags_series = hashtags_series[hashtags_series != '[]']  # Eliminar listas vacías
    hashtags_fig = px.bar(hashtags_series.value_counts().head(10), title='Top 10 Hashtags Usados')
    hashtags_fig.update_xaxes(title='Hashtags', tickmode='array', tickvals=[])
    hashtags_fig.update_yaxes(title='Frecuencia')
    hashtags_fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(hashtags_fig, use_container_width=True)

# Análisis de Publicaciones por Hora
with col2:
    st.subheader("Publicaciones por Hora del Día")
    df_filtered['hour'] = df_filtered['date'].dt.hour
    posts_by_hour_fig = px.histogram(df_filtered, x='hour', nbins=24, title='Publicaciones por Hora del Día')
    posts_by_hour_fig.update_xaxes(title='Hora del Día')
    posts_by_hour_fig.update_yaxes(title='Número de Publicaciones')
    posts_by_hour_fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(posts_by_hour_fig, use_container_width=True)

# Nube de palabras de captions
st.header("Nube de Palabras de Captions")
text = " ".join(clean_text(caption) for caption in df_filtered['caption'].dropna())

# Crear y mostrar la nube de palabras
wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='viridis', stopwords=stopwords).generate(text)

# Mostrar la nube de palabras en Streamlit
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis("off")
st.pyplot(fig)

