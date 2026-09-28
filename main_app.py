import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Desempeño Estudiantil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Análisis de Desempeño Estudiantil")
st.markdown("---")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv('medio.csv')
    return df

try:
    df = load_data()
    
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de participación
    participacion_options = ['Todos'] + sorted(df['participacion_clase'].unique().tolist())
    participacion_selected = st.sidebar.selectbox(
        "Participación en clase",
        participacion_options
    )
    
    # Filtro de horario
    horario_options = ['Todos'] + sorted(df['horario_estudio'].unique().tolist())
    horario_selected = st.sidebar.selectbox(
        "Horario de estudio",
        horario_options
    )
    
    # Rango de nota final
    nota_min, nota_max = st.sidebar.slider(
        "Rango de nota final",
        float(df['nota_final'].min()),
        float(df['nota_final'].max()),
        (float(df['nota_final'].min()), float(df['nota_final'].max())),
        step=0.1
    )
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if participacion_selected != 'Todos':
        df_filtered = df_filtered[df_filtered['participacion_clase'] == participacion_selected]
    
    if horario_selected != 'Todos':
        df_filtered = df_filtered[df_filtered['horario_estudio'] == horario_selected]
    
    df_filtered = df_filtered[
        (df_filtered['nota_final'] >= nota_min) & 
        (df_filtered['nota_final'] <= nota_max)
    ]
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Estudiantes",
            len(df_filtered),
            f"de {len(df)}"
        )
    
    with col2:
        promedio = df_filtered['nota_final'].mean()
        st.metric(
            "Promedio Notas",
            f"{promedio:.2f}",
            f"(Gral: {df['nota_final'].mean():.2f})"
        )
    
    with col3:
        mediana = df_filtered['nota_final'].median()
        st.metric(
            "Mediana Notas",
            f"{mediana:.2f}",
            f"(Gral: {df['nota_final'].median():.2f})"
        )
    
    with col4:
        desviacion = df_filtered['nota_final'].std()
        st.metric(
            "Desv. Estándar",
            f"{desviacion:.2f}",
            f"(Gral: {df['nota_final'].std():.2f})"
        )
    
    st.markdown("---")
    
    # Visualizaciones
    col1, col2 = st.columns(2)
    
    # Distribución de notas
    with col1:
        st.subheader("Distribución de Notas Finales")
        fig_hist = px.histogram(
            df_filtered,
            x='nota_final',
            nbins=20,
            title="",
            labels={'nota_final': 'Nota Final', 'count': 'Cantidad Estudiantes'},
            color_discrete_sequence=['#636EFA']
        )
        fig_hist.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Notas por participación
    with col2:
        st.subheader("Nota Promedio por Participación")
        avg_por_participacion = df_filtered.groupby('participacion_clase')['nota_final'].agg(['mean', 'count']).reset_index()
        avg_por_participacion = avg_por_participacion.sort_values('mean', ascending=False)
        
        fig_par = px.bar(
            avg_por_participacion,
            x='participacion_clase',
            y='mean',
            title="",
            labels={'participacion_clase': 'Participación', 'mean': 'Nota Promedio'},
            text='count',
            color_discrete_sequence=['#00CC96']
        )
        fig_par.update_traces(texttemplate='n=%{text}', textposition='outside')
        fig_par.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_par, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    # Notas por horario
    with col1:
        st.subheader("Nota Promedio por Horario de Estudio")
        avg_por_horario = df_filtered.groupby('horario_estudio')['nota_final'].agg(['mean', 'count']).reset_index()
        
        fig_hor = px.bar(
            avg_por_horario,
            x='horario_estudio',
            y='mean',
            title="",
            labels={'horario_estudio': 'Horario', 'mean': 'Nota Promedio'},
            text='count',
            color_discrete_sequence=['#AB63FA']
        )
        fig_hor.update_traces(texttemplate='n=%{text}', textposition='outside')
        fig_hor.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_hor, use_container_width=True)
    
    # Matriz de relaciones
    with col2:
        st.subheader("Relación Participación × Horario")
        matriz = pd.crosstab(
            df_filtered['participacion_clase'],
            df_filtered['horario_estudio'],
            margins=True
        )
        st.dataframe(matriz, use_container_width=True)
    
    st.markdown("---")
    
    # Análisis detallado por participación y horario
    st.subheader("📈 Análisis Detallado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Box plot por participación
        fig_box_par = px.box(
            df_filtered,
            x='participacion_clase',
            y='nota_final',
            title="Distribución de Notas por Participación",
            labels={'participacion_clase': 'Participación', 'nota_final': 'Nota Final'},
            color_discrete_sequence=['#FFA15A']
        )
        fig_box_par.update_layout(height=450)
        st.plotly_chart(fig_box_par, use_container_width=True)
    
    with col2:
        # Box plot por horario
        fig_box_hor = px.box(
            df_filtered,
            x='horario_estudio',
            y='nota_final',
            title="Distribución de Notas por Horario",
            labels={'horario_estudio': 'Horario', 'nota_final': 'Nota Final'},
            color_discrete_sequence=['#00CC96']
        )
        fig_box_hor.update_layout(height=450)
        st.plotly_chart(fig_box_hor, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla de datos con opciones
    st.subheader("📋 Datos Detallados")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        descargar = st.checkbox("Descargar CSV filtrado")
    
    st.dataframe(df_filtered, use_container_width=True, height=400)
    
    if descargar:
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="Descargar datos filtrados",
            data=csv,
            file_name="datos_filtrados.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    
    # Estadísticas resumidas
    with st.expander("📊 Estadísticas Resumidas"):
        st.write("**Estadísticas por Participación:**")
        stats_par = df_filtered.groupby('participacion_clase')['nota_final'].agg([
            ('Cantidad', 'count'),
            ('Promedio', 'mean'),
            ('Mínima', 'min'),
            ('Máxima', 'max'),
            ('Desv. Est.', 'std')
        ]).round(2)
        st.dataframe(stats_par, use_container_width=True)
        
        st.write("\n**Estadísticas por Horario:**")
        stats_hor = df_filtered.groupby('horario_estudio')['nota_final'].agg([
            ('Cantidad', 'count'),
            ('Promedio', 'mean'),
            ('Mínima', 'min'),
            ('Máxima', 'max'),
            ('Desv. Est.', 'std')
        ]).round(2)
        st.dataframe(stats_hor, use_container_width=True)

except FileNotFoundError:
    st.error("⚠️ El archivo 'medio.csv' no se encontró. Asegúrate de que está en el mismo directorio que main_app.py")
except Exception as e:
    st.error(f"❌ Error al procesar el archivo: {str(e)}")
