# data_handler.py
import pandas as pd
import requests
from datetime import datetime
import pytz

class DataHandler:
    def __init__(self):
        self.dados = pd.DataFrame()
        self.ativo_selecionado = None
        self.timezone = pytz.timezone("America/Sao_Paulo")

    def buscar_dados_binance(self, ativo, intervalo="1m", limite=200):
        """Busca dados da Binance e armazena as últimas N velas."""
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={ativo}&interval={intervalo}&limit={limite}"
            response = requests.get(url).json()
            
            # Processar dados
            colunas = ["timestamp", "open", "high", "low", "close", "volume", "close_time", 
                       "quote_volume", "trades", "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
            self.dados = pd.DataFrame(response, columns=colunas)
            
            # Converter timestamp para GMT-3 e ajustar colunas
            self.dados["timestamp"] = self.dados["timestamp"].apply(
                lambda x: datetime.fromtimestamp(x / 1000, tz=self.timezone).strftime("%H:%M:%S")
            )
            self.dados = self.dados[["timestamp", "open", "high", "low", "close", "volume"]].astype({
                "open": float, "high": float, "low": float, "close": float, "volume": float
            })
            
            self.ativo_selecionado = ativo
            return True
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            return False

    def obter_ultima_vela(self):
        """Retorna a última vela do DataFrame."""
        if not self.dados.empty:
            return self.dados.iloc[-1].to_dict()
        return None

    def obter_tempo_restante(self):
        """Calcula o tempo restante para o fechamento da vela atual (em segundos)."""
        if not self.dados.empty:
            agora = datetime.now(self.timezone)
            ultima_vela = datetime.strptime(self.dados.iloc[-1]["timestamp"], "%H:%M:%S").replace(
                year=agora.year, month=agora.month, day=agora.day, tzinfo=self.timezone
            )
            tempo_restante = (ultima_vela + pd.Timedelta(minutes=1) - agora).total_seconds()
            return max(0, int(tempo_restante))
        return 0
