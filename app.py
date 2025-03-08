# app.py
import streamlit as st
import time
from datetime import datetime, timedelta
import pytz
from data_handler import DataHandler
from indicators import Indicators

# Configuração inicial
st.set_page_config(layout="wide")

# Estilos CSS personalizados
st.markdown(
    """
    <style>
    .main {background-color: #292A2D; color: #FFFFFF;}
    .stSelectbox div {background-color: #454545;}
    .stButton button {background-color: #4CAF50; color: white;}
    .stButton button:disabled {background-color: #ff0000;}
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
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'scores' not in st.session_state:
    st.session_state.scores = {'acertos': 0, 'erros_compra': 0, 'erros_venda': 0}

# Instância dos módulos
data_handler = DataHandler()
indicators = None

# Função para obter lista de ativos da API
def carregar_ativos():
    # Implementação temporária - necessário integração com API real
    return ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT"]

# Header da aplicação
col1, col2, col3 = st.columns([2,1,1])
with col1:
    ativo = st.selectbox("ATIVO:", carregar_ativos(), key="ativo_select")

# Controle principal
def toggle_execucao():
    st.session_state.running = not st.session_state.running
    st.session_state.last_activity = datetime.now(pytz.timezone("America/Sao_Paulo"))
    if st.session_state.running:
        st.session_state.start_time = datetime.now(pytz.timezone("America/Sao_Paulo"))
        st.session_state.ativo = ativo

# Atualização de dados em tempo real
def atualizar_dados():
    if data_handler.buscar_dados_binance(st.session_state.ativo):
        global indicators
        indicators = Indicators(data_handler.dados)
        indicators.calcular_indicadores()
        indicators.detectar_padroes()

# Interface principal
col2, col3 = st.columns(2)
with col2:
    btn_label = "PARAR" if st.session_state.running else "INICIAR"
    if st.button(btn_label, key="exec_button", on_click=toggle_execucao):
        st.experimental_rerun()

# Componentes de tempo
def atualizar_tempos():
    agora = datetime.now(pytz.timezone("America/Sao_Paulo"))
    tempo_restante = data_handler.obter_tempo_restante() if st.session_state.running else 0
    
    with col3:
        st.markdown(f"""
        **RELÓGIO:** {agora.strftime("%H:%M:%S")}  
        **TEMPO RESTANTE:** {tempo_restante}s
        """)

# Exibição de sinais
def exibir_sinais():
    compra, venda = indicators.gerar_sinal() if indicators else (0, 0)
    cor_compra = "#0bed07" if compra > venda else "#FFFFFF"
    cor_venda = "#ff0000" if venda > compra else "#FFFFFF"
    
    st.markdown(f"""
    <div style="font-size:22px; color:{cor_compra};">COMPRAR {compra}%</div>
    <div style="font-size:22px; color:{cor_venda};">VENDER {venda}%</div>
    """, unsafe_allow_html=True)

# Placar de resultados
def exibir_placar():
    st.markdown(f"""
    **PLACAR:**  
    ✅ Acertos: {st.session_state.scores['acertos']}  
    ❌ Erros Compra: {st.session_state.scores['erros_compra']}  
    ❌ Erros Venda: {st.session_state.scores['erros_venda']}
    """)

# Loop principal da aplicação
if st.session_state.running:
    # Verificar inatividade
    inatividade = (datetime.now(pytz.timezone("America/Sao_Paulo")) - st.session_state.last_activity)
    if inatividade > timedelta(minutes=15):
        st.session_state.running = False
        st.experimental_rerun()
    
    # Atualizar dados a cada 15s
    if (datetime.now(pytz.timezone("America/Sao_Paulo")) - st.session_state.last_activity).seconds % 15 == 0:
        atualizar_dados()
    
    # Exibir componentes
    atualizar_tempos()
    exibir_sinais()
    exibir_placar()
    
    # Manter atualização automática
    time.sleep(1)
    st.experimental_rerun()

else:
    st.info("Aplicação parada. Selecione um ativo e clique em INICIAR.")
