import pandas as pd
import pandas_ta as ta

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
            df['EMA9'] = ta.ema(df['close'], length=9)
            df['EMA21'] = ta.ema(df['close'], length=21)
            df['RSI'] = ta.rsi(df['close'], length=14)
            df['MACD'] = ta.macd(df['close'], fast=12, slow=26, signal=9)['MACD_12_26_9']
            bbands = ta.bbands(df['close'], length=20)
            df['Bollinger_Upper'] = bbands['BBU_20_2.0']
            df['Bollinger_Lower'] = bbands['BBL_20_2.0']
            df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
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
