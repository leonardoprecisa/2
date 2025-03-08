import pandas as pd
import talib

class Indicators:
    def __init__(self, dados):
        self.dados = dados
        self.pesos_indicadores = {
            "EMA": 0.15, "RSI": 0.10, "MACD": 0.15, 
            "Bollinger": 0.10, "Volume": 0.05, "ATR": 0.05
        }

    def calcular_indicadores(self):
        try:
            df = self.dados
            # Indicadores de Compra
            df['EMA9'] = talib.EMA(df['close'], timeperiod=9)
            df['EMA21'] = talib.EMA(df['close'], timeperiod=21)
            df['RSI'] = talib.RSI(df['close'], timeperiod=14)
            df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(
                df['close'], fastperiod=12, slowperiod=26, signalperiod=9
            )
            df['Bollinger_Upper'], df['Bollinger_Middle'], df['Bollinger_Lower'] = talib.BBANDS(
                df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
            )
            df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            return True
        except Exception as e:
            print(f"Erro ao calcular indicadores: {e}")
            return False

    def gerar_sinal(self):
        sinal_compra = 0
        sinal_venda = 0
        
        # Lógica para Compra
        if self.dados['EMA9'].iloc[-1] > self.dados['EMA21'].iloc[-1]:
            sinal_compra += self.pesos_indicadores["EMA"] * 100
        if self.dados['RSI'].iloc[-1] < 30:
            sinal_compra += self.pesos_indicadores["RSI"] * 100
        if self.dados['MACD'].iloc[-1] > 0:
            sinal_compra += self.pesos_indicadores["MACD"] * 100
            
        # Limitar a 100%
        return (
            min(100, round(sinal_compra, 2)), 
            min(100, round(sinal_venda, 2)
        )
