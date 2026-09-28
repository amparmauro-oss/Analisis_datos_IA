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

# CSS personalizado
st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #1f77b4;
        }
        .metric-card {
            padding: 15px;
            border-radius: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv('medio.csv')
    return df

try:
    df = load_data()
    
    # ==================== SIDEBAR ====================
    st.sidebar.image("https://via.placeholder.com/200x50?text=Logo", use_container_width=True)
    st.sidebar.title("🎛️ PANEL DE CONTROL")
    st.sidebar.markdown("---")
    
    # Sección 1: VISTA GENERAL
    with st.sidebar.expander("📊 VISTA GENERAL", expanded=True):
        st.write("**Total de registros:** " + str(len(df)))
        st.write("**Rango de notas:** " + f"{df['nota_final'].min():.1f} - {df['nota_final'].max():.1f}")
        if st.button("🔄 Recargar datos", key="reload"):
            st.cache_data.clear()
            st.rerun()
    
    # Sección 2: FILTROS
    st.sidebar.markdown("---")
    with st.sidebar.expander("🔍 FILTROS RÁPIDOS", expanded=True):
        
        st.write("**Participación en clase:**")
        participacion_options = ['Todos'] + sorted(df['participacion_clase'].unique().tolist())
        participacion_selected = st.selectbox(
            "Selecciona participación",
            participacion_options,
            key="part"
        )
        
        st.write("**Horario de estudio:**")
        horario_options = ['Todos'] + sorted(df['horario_estudio'].unique().tolist())
        horario_selected = st.selectbox(
            "Selecciona horario",
            horario_options,
            key="hor"
        )
        
        st.write("**Rango de nota final:**")
        nota_min, nota_max = st.slider(
            "Nota mínima y máxima",
            float(df['nota_final'].min()),
            float(df['nota_final'].max()),
            (float(df['nota_final'].min()), float(df['nota_final'].max())),
            step=0.1,
            key="nota_range"
        )
        
        # Botón para limpiar filtros
        if st.button("🗑️ Limpiar filtros", use_container_width=True):
            st.session_state.part = 'Todos'
            st.session_state.hor = 'Todos'
            st.session_state.nota_range = (float(df['nota_final'].min()), float(df['nota_final'].max()))
            st.rerun()
    
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
    
    # Sección 3: OPCIONES DE ANÁLISIS
    st.sidebar.markdown("---")
    with st.sidebar.expander("📈 TIPO DE ANÁLISIS", expanded=True):
        tipo_analisis = st.radio(
            "Selecciona el análisis a mostrar:",
            ["Dashboard General", "Análisis Participación", "Análisis Horario", "Análisis Cruzado", "Datos Detallados"],
            key="tipo_analisis"
        )
    
    # Sección 4: OPCIONES DE VISUALIZACIÓN
    st.sidebar.markdown("---")
    with st.sidebar.expander("🎨 VISUALIZACIÓN", expanded=False):
        tipo_grafico = st.selectbox(
            "Tipo de gráfico para histograma:",
            ["Histograma", "Gráfico de barras", "Gráfico de densidad"],
            key="tipo_graf"
        )
        
        mostrar_media = st.checkbox("Mostrar línea de media", value=True)
        mostrar_mediana = st.checkbox("Mostrar línea de mediana", value=True)
        paleta_colores = st.selectbox(
            "Paleta de colores:",
            ["Plotly", "Viridis", "Reds", "Blues", "Greens"],
            key="paleta"
        )
    
    # Sección 5: DESCARGAS
    st.sidebar.markdown("---")
    with st.sidebar.expander("📥 DESCARGAS", expanded=False):
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="📊 Descargar CSV Filtrado",
            data=csv,
            file_name="datos_filtrados.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Sección 6: INFORMACIÓN
    st.sidebar.markdown("---")
    with st.sidebar.expander("ℹ️ INFORMACIÓN", expanded=False):
        st.info("""
        **Guía de uso:**
        - Usa los filtros para segmentar datos
        - Selecciona el tipo de análisis
        - Personaliza la visualización
        - Descarga los datos según necesites
        """)
    
    # ==================== CONTENIDO PRINCIPAL ====================
    st.markdown("# 📊 Análisis de Desempeño Estudiantil")
    st.markdown(f"Registros mostrados: **{len(df_filtered)} de {len(df)}**")
    st.markdown("---")
    
    # MÉTRICAS PRINCIPALES
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "👥 Total Estudiantes",
            len(df_filtered),
            f"filtrados de {len(df)}"
        )
    
    with col2:
        promedio = df_filtered['nota_final'].mean()
        delta_prom = promedio - df['nota_final'].mean()
        st.metric(
            "📈 Promedio Notas",
            f"{promedio:.2f}",
            f"{delta_prom:+.2f}",
            delta_color="off"
        )
    
    with col3:
        mediana = df_filtered['nota_final'].median()
        st.metric(
            "📊 Mediana Notas",
            f"{mediana:.2f}",
            f"(Gral: {df['nota_final'].median():.2f})"
        )
    
    with col4:
        desviacion = df_filtered['nota_final'].std()
        st.metric(
            "📉 Desv. Estándar",
            f"{desviacion:.2f}",
            f"(Gral: {df['nota_final'].std():.2f})"
        )
    
    st.markdown("---")
    
    # CONTENIDO SEGÚN TIPO DE ANÁLISIS
    
    if tipo_analisis == "Dashboard General":
        st.subheader("📋 Dashboard General")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Distribución de Notas Finales**")
            if tipo_grafico == "Histograma":
                fig_hist = px.histogram(df_filtered, x='nota_final', nbins=20, 
                                       color_discrete_sequence=['#636EFA'])
            elif tipo_grafico == "Gráfico de barras":
                fig_hist = px.bar(df_filtered.groupby(pd.cut(df_filtered['nota_final'], bins=10)).size().reset_index(drop=True),
                                 color_discrete_sequence=['#636EFA'])
            else:
                fig_hist = px.density_histogram(df_filtered, x='nota_final',
                                               color_discrete_sequence=['#636EFA'])
            
            if mostrar_media:
                fig_hist.add_vline(df_filtered['nota_final'].mean(), line_dash="dash", 
                                 line_color="red", annotation_text="Media")
            if mostrar_mediana:
                fig_hist.add_vline(df_filtered['nota_final'].median(), line_dash="dash", 
                                 line_color="green", annotation_text="Mediana")
            
            fig_hist.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.write("**Estadísticas Rápidas**")
            stats_data = {
                'Métrica': ['Mínimo', 'Q1', 'Mediana', 'Q3', 'Máximo'],
                'Valor': [
                    f"{df_filtered['nota_final'].min():.2f}",
                    f"{df_filtered['nota_final'].quantile(0.25):.2f}",
                    f"{df_filtered['nota_final'].median():.2f}",
                    f"{df_filtered['nota_final'].quantile(0.75):.2f}",
                    f"{df_filtered['nota_final'].max():.2f}"
                ]
            }
            st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Promedio por Participación**")
            avg_par = df_filtered.groupby('participacion_clase')['nota_final'].agg(['mean', 'count']).reset_index().sort_values('mean', ascending=False)
            fig_par = px.bar(avg_par, x='participacion_clase', y='mean', text='count',
                            color_discrete_sequence=['#00CC96'])
            fig_par.update_traces(texttemplate='n=%{text}', textposition='outside')
            fig_par.update_layout(height=400, showlegend=False, xaxis_title="Participación", yaxis_title="Nota Promedio")
            st.plotly_chart(fig_par, use_container_width=True)
        
        with col2:
            st.write("**Promedio por Horario**")
            avg_hor = df_filtered.groupby('horario_estudio')['nota_final'].agg(['mean', 'count']).reset_index()
            fig_hor = px.bar(avg_hor, x='horario_estudio', y='mean', text='count',
                            color_discrete_sequence=['#AB63FA'])
            fig_hor.update_traces(texttemplate='n=%{text}', textposition='outside')
            fig_hor.update_layout(height=400, showlegend=False, xaxis_title="Horario", yaxis_title="Nota Promedio")
            st.plotly_chart(fig_hor, use_container_width=True)
    
    elif tipo_analisis == "Análisis Participación":
        st.subheader("🎓 Análisis Detallado por Participación")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Box Plot por Participación**")
            fig_box = px.box(df_filtered, x='participacion_clase', y='nota_final',
                            color_discrete_sequence=['#FFA15A'])
            fig_box.update_layout(height=450, xaxis_title="Participación", yaxis_title="Nota Final")
            st.plotly_chart(fig_box, use_container_width=True)
        
        with col2:
            st.write("**Distribución por Participación**")
            fig_violin = px.violin(df_filtered, x='participacion_clase', y='nota_final',
                                  color_discrete_sequence=['#FF6B6B'])
            fig_violin.update_layout(height=450, xaxis_title="Participación", yaxis_title="Nota Final")
            st.plotly_chart(fig_violin, use_container_width=True)
        
        st.write("**Tabla de Estadísticas por Participación**")
        stats_par = df_filtered.groupby('participacion_clase')['nota_final'].agg([
            ('Cantidad', 'count'),
            ('Promedio', 'mean'),
            ('Mínima', 'min'),
            ('Máxima', 'max'),
            ('Desv. Est.', 'std')
        ]).round(2)
        st.dataframe(stats_par, use_container_width=True)
    
    elif tipo_analisis == "Análisis Horario":
        st.subheader("⏰ Análisis Detallado por Horario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Box Plot por Horario**")
            fig_box = px.box(df_filtered, x='horario_estudio', y='nota_final',
                            color_discrete_sequence=['#4ECDC4'])
            fig_box.update_layout(height=450, xaxis_title="Horario", yaxis_title="Nota Final")
            st.plotly_chart(fig_box, use_container_width=True)
        
        with col2:
            st.write("**Distribución por Horario**")
            fig_violin = px.violin(df_filtered, x='horario_estudio', y='nota_final',
                                  color_discrete_sequence=['#95E1D3'])
            fig_violin.update_layout(height=450, xaxis_title="Horario", yaxis_title="Nota Final")
            st.plotly_chart(fig_violin, use_container_width=True)
        
        st.write("**Tabla de Estadísticas por Horario**")
        stats_hor = df_filtered.groupby('horario_estudio')['nota_final'].agg([
            ('Cantidad', 'count'),
            ('Promedio', 'mean'),
            ('Mínima', 'min'),
            ('Máxima', 'max'),
            ('Desv. Est.', 'std')
        ]).round(2)
        st.dataframe(stats_hor, use_container_width=True)
    
    elif tipo_analisis == "Análisis Cruzado":
        st.subheader("🔀 Análisis Cruzado: Participación × Horario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Matriz de Relaciones**")
            matriz = pd.crosstab(
                df_filtered['participacion_clase'],
                df_filtered['horario_estudio'],
                margins=True
            )
            st.dataframe(matriz, use_container_width=True)
        
        with col2:
            st.write("**Promedio de Notas (Participación × Horario)**")
            matriz_notas = pd.pivot_table(
                df_filtered,
                values='nota_final',
                index='participacion_clase',
                columns='horario_estudio',
                aggfunc='mean'
            )
            st.dataframe(matriz_notas.round(2), use_container_width=True)
        
        st.write("**Heatmap de Notas Promedio**")
        fig_heatmap = px.imshow(
            matriz_notas,
            labels=dict(x="Horario", y="Participación", color="Nota Promedio"),
            color_continuous_scale="RdYlGn",
            text_auto='.2f'
        )
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        st.write("**Gráfico de Barras Agrupado**")
        df_plot = df_filtered.groupby(['participacion_clase', 'horario_estudio'])['nota_final'].mean().reset_index()
        fig_grouped = px.bar(
            df_plot,
            x='participacion_clase',
            y='nota_final',
            color='horario_estudio',
            barmode='group',
            labels={'nota_final': 'Nota Promedio', 'participacion_clase': 'Participación', 'horario_estudio': 'Horario'}
        )
        fig_grouped.update_layout(height=400)
        st.plotly_chart(fig_grouped, use_container_width=True)
    
    elif tipo_analisis == "Datos Detallados":
        st.subheader("📋 Tabla Completa de Datos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            orden = st.selectbox("Ordenar por:", df_filtered.columns)
        with col2:
            direccion = st.radio("Dirección:", ["Ascendente ↑", "Descendente ↓"], horizontal=True)
        with col3:
            if st.button("🔄 Aplicar orden", use_container_width=True):
                ascending = direccion == "Ascendente ↑"
                df_filtered = df_filtered.sort_values(by=orden, ascending=ascending)
        
        st.write(f"**Total de registros: {len(df_filtered)}**")
        st.dataframe(df_filtered, use_container_width=True, height=500)
        
        st.write("**Resumen por columna:**")
        for col in df_filtered.columns:
            if df_filtered[col].dtype in ['float64', 'int64']:
                st.write(f"**{col}**: min={df_filtered[col].min():.2f}, max={df_filtered[col].max():.2f}, promedio={df_filtered[col].mean():.2f}")
            else:
                st.write(f"**{col}**: {df_filtered[col].nunique()} valores únicos")

except FileNotFoundError:
    st.error("⚠️ El archivo 'medio.csv' no se encontró. Asegúrate de que está en el mismo directorio que main_app.py")
except Exception as e:
    st.error(f"❌ Error al procesar el archivo: {str(e)}")
