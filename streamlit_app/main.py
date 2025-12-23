import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path

# Agregar src al path
current_dir = Path(__file__).parent
src_path = current_dir.parent / "src"
sys.path.insert(0, str(src_path))

# Importar nuestros módulos
try:
    from data_processor import DataProcessor
    from competitive_analyzer import CompetitiveAnalyzer
    from hotel_agent import HotelAgent
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()

# Configuración de página
st.set_page_config(
    page_title="Hotel Competitiveness Agent",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #2E86AB;
        background-color: #F8F9FA;
    }
    .metric-card {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">🏨 Hotel Competitiveness Agent</h1>', unsafe_allow_html=True)

# Inicialización de estado
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_hotel' not in st.session_state:
    st.session_state.current_hotel = None

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Cargar datos
    st.subheader("📁 Cargar Datos")
    
    uploaded_internal = st.file_uploader(
        "Hound Internal CSV", 
        type=['csv'],
        key="internal"
    )
    
    uploaded_external = st.file_uploader(
        "Hound External CSV", 
        type=['csv'],
        key="external"
    )
    
    uploaded_extranet = st.file_uploader(
        "Extranet CSV", 
        type=['csv'],
        key="extranet"
    )
    
    # Botón para procesar datos
    if st.button("🔄 Cargar y Procesar Datos"):
        if uploaded_internal and uploaded_external and uploaded_extranet:
            try:
                with st.spinner("Cargando datos..."):
                    # Guardar archivos temporalmente
                    temp_dir = Path("temp")
                    temp_dir.mkdir(exist_ok=True)
                    
                    internal_path = temp_dir / "internal.csv"
                    external_path = temp_dir / "external.csv"
                    extranet_path = temp_dir / "extranet.csv"
                    
                    with open(internal_path, "wb") as f:
                        f.write(uploaded_internal.read())
                    with open(external_path, "wb") as f:
                        f.write(uploaded_external.read())
                    with open(extranet_path, "wb") as f:
                        f.write(uploaded_extranet.read())
                    
                    # Inicializar procesador
                    dp = DataProcessor()
                    success = dp.load_data(
                        str(internal_path),
                        str(external_path), 
                        str(extranet_path)
                    )
                    
                    if success:
                        # Inicializar analizador y agente
                        ca = CompetitiveAnalyzer(dp)
                        agent = HotelAgent(dp, ca)
                        
                        st.session_state.data_processor = dp
                        st.session_state.competitive_analyzer = ca
                        st.session_state.agent = agent
                        st.session_state.data_loaded = True
                        
                        st.success("✅ Datos cargados exitosamente!")
                        st.rerun()
                    else:
                        st.error("❌ Error cargando datos")
                        
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("⚠️ Sube los 3 archivos CSV requeridos")
    
    # Status
    if st.session_state.data_loaded:
        st.success("✅ Datos cargados")
        
        # Selector de hotel
        if st.session_state.agent:
            hotels = st.session_state.agent.dp.get_available_hotels()
            if hotels:
                selected_hotel = st.selectbox(
                    "🏨 Seleccionar Hotel",
                    hotels,
                    key="hotel_selector"
                )
                
                if selected_hotel != st.session_state.current_hotel:
                    st.session_state.current_hotel = selected_hotel
                    st.session_state.agent.current_hotel = selected_hotel
                    
    else:
        st.warning("⚠️ Datos no cargados")

# Área principal
if not st.session_state.data_loaded:
    # Pantalla de bienvenida
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### 🚀 Bienvenido al Hotel Competitiveness Agent
        
        Este agente de IA te ayuda a:
        
        ✅ **Analizar competitividad** de tus hoteles  
        ✅ **Comparar precios** con competidores  
        ✅ **Identificar oportunidades** por mercado  
        ✅ **Simular impacto** de cambios de precio  
        ✅ **Generar recomendaciones** estratégicas  
        
        **Para empezar:**
        1. Sube los 3 archivos CSV en la barra lateral
        2. Haz clic en "Cargar y Procesar Datos"
        3. ¡Comienza a conversar con el agente!
        """)
        
        # Demo de comandos
        with st.expander("📋 Ver comandos disponibles"):
            st.code("""
# Selección de hotel
"seleccionar hotel Crown Paradise"
"ver hoteles disponibles"

# Análisis
"análisis de competitividad"
"comparar precios"
"analizar mercados"

# Recomendaciones y simulaciones
"dame recomendaciones"
"simular -10%"
"análisis cross market"
            """, language="text")

else:
    # Interface principal del chat
    
    # Métricas rápidas si hay hotel seleccionado
    if st.session_state.current_hotel and st.session_state.agent:
        st.subheader(f"📊 {st.session_state.current_hotel}")
        
        summary = st.session_state.agent.dp.get_hotel_summary(st.session_state.current_hotel)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Score Competitividad",
                f"{summary.get('competitiveness_score', 0)}/100",
                delta=None
            )
        
        with col2:
            avg_diff = summary.get('avg_price_difference_pct', 0)
            st.metric(
                "Diferencia Promedio",
                f"{avg_diff:+.1f}%",
                delta=f"{'Ganamos' if avg_diff < 0 else 'Perdemos'}"
            )
        
        with col3:
            st.metric(
                "Búsquedas Totales",
                f"{summary.get('total_searches', 0):,}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Mercados Activos",
                len(summary.get('markets_pos', [])),
                delta=None
            )
    
    st.markdown("---")
    
    # Chat interface
    st.subheader("💬 Chat con el Agente")
    
    # Historial de chat
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"""
                <div style="text-align: right; margin: 10px 0;">
                    <div style="display: inline-block; background-color: #2E86AB; color: white; 
                                padding: 10px; border-radius: 15px; max-width: 80%;">
                        <strong>Tú:</strong> {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: left; margin: 10px 0;">
                    <div style="display: inline-block; background-color: #F0F0F0; 
                                padding: 10px; border-radius: 15px; max-width: 80%;">
                        <strong>🤖 Agente:</strong><br>{message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar gráfico si existe
                if "chart" in message and message["chart"]:
                    st.plotly_chart(message["chart"], use_container_width=True)
    
    # Input del usuario
    user_input = st.text_input(
        "Escribe tu consulta aquí...",
        placeholder="Ej: análisis de competitividad, comparar precios, simular -10%",
        key="user_input"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        send_button = st.button("📤 Enviar", use_container_width=True)
    
    with col2:
        # Botones rápidos
        quick_buttons = st.columns(4)
        with quick_buttons[0]:
            if st.button("📊 Competitividad", use_container_width=True):
                user_input = "análisis de competitividad"
                send_button = True
        with quick_buttons[1]:
            if st.button("💰 Precios", use_container_width=True):
                user_input = "comparar precios"
                send_button = True
        with quick_buttons[2]:
            if st.button("🌍 Mercados", use_container_width=True):
                user_input = "analizar mercados"
                send_button = True
        with quick_buttons[3]:
            if st.button("💡 Tips", use_container_width=True):
                user_input = "dame recomendaciones"
                send_button = True
    
    # Procesar input
    if send_button and user_input and st.session_state.agent:
        # Agregar mensaje del usuario al historial
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Procesar con el agente
        with st.spinner("🤔 Procesando..."):
            response = st.session_state.agent.process_query(user_input)
        
        # Agregar respuesta al historial
        agent_message = {
            "role": "agent",
            "content": response.message
        }
        
        if response.chart:
            agent_message["chart"] = response.chart
        
        st.session_state.chat_history.append(agent_message)
        
        # Limpiar input y refrescar
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    🏨 Hotel Competitiveness Agent | Powered by Streamlit & Python
</div>
""", unsafe_allow_html=True)
