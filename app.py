import streamlit as st
import time
from datetime import datetime, timedelta
import pytz
from data_handler import DataHandler
from indicators import Indicators

# Configuração inicial
st.set_page_config(layout="wide")

# Estilos CSS
st.markdown(
    """
    <style>
    .main {background-color: #292A2D; color: #FFFFFF;}
    .stSelectbox div {background-color: #454545;}
    .stButton button {background-color: #4CAF50; color: white;}
    .signal-box {padding: 20px; border-radius: 10px; margin: 10px 0;}
    </style>
    """,
    unsafe_allow_html=True
)

# Inicialização do Session State
if 'running' not in st.session_state:
    st.session_state.running = False
if 'ativo' not in st.session_state:
    st.session_state.ativo = None
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = datetime.now(pytz.timezone("America/Sao_Paulo"))
if 'scores' not in st.session_state:
    st.session_state.scores = {'acertos': 0, 'erros_compra': 0, 'erros_venda': 0}

# Instância dos módulos
data_handler = DataHandler()
indicators = None

# Placeholders para atualização dinâmica
time_placeholder = st.empty()
signal_placeholder = st.empty()
status_placeholder = st.empty()

def carregar_ativos():
    """Lista de ativos (exemplo estático)"""
    return ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT"]

def atualizar_interface():
    """Atualiza a interface sem recriar componentes"""
    agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
    tempo_restante = data_handler.obter_tempo_restante() if st.session_state.running else 0
    
    # Atualizar relógio e tempo restante
    with time_placeholder:
        st.markdown(f"""
        **RELÓGIO:** {agora.strftime("%H:%M:%S")}  
        **TEMPO RESTANTE:** {tempo_restante}s
        """)
    
    # Atualizar sinais
    if indicators:
        compra, venda = indicators.gerar_sinal()
        cor_compra = "#0bed07" if compra > venda else "#FFFFFF"
        cor_venda = "#ff0000" if venda > compra else "#FFFFFF"
        
        with signal_placeholder:
            st.markdown(f"""
            <div style="font-size:22px; color:{cor_compra};">COMPRAR {compra}%</div>
            <div style="font-size:22px; color:{cor_venda};">VENDER {venda}%</div>
            """, unsafe_allow_html=True)

def toggle_execucao():
    """Controla o estado de execução"""
    st.session_state.running = not st.session_state.running
    st.session_state.last_activity = datetime.now(pytz.timezone("America/Sao_Paulo"))

# Interface
col1, col2 = st.columns([2, 1])
with col1:
    ativo = st.selectbox("ATIVO:", carregar_ativos())

with col2:
    btn_label = "PARAR" if st.session_state.running else "INICIAR"
    if st.button(btn_label, on_click=toggle_execucao):
        st.session_state.ativo = ativo

# Lógica principal
if st.session_state.running:
    # Verificar inatividade
    if (datetime.now(pytz.timezone("America/Sao_Paulo")) - st.session_state.last_activity > timedelta(minutes=15):
        st.session_state.running = False
        st.experimental_rerun()
    
    # Atualizar dados a cada 15s
    if data_handler.buscar_dados_binance(st.session_state.ativo):
        indicators = Indicators(data_handler.dados)
        indicators.calcular_indicadores()
        indicators.detectar_padroes()
    
    atualizar_interface()
else:
    status_placeholder.info("Aplicação parada. Clique em INICIAR para começar.")
