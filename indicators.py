import pandas as pd
import talib

class Indicators:
    def __init__(self, dados):
        """
        Inicializa a classe com os dados fornecidos.
        
        :param dados: DataFrame contendo os dados do ativo (timestamp, open, high, low, close, volume).
        """
        self.dados = dados
        self.padroes_detectados = []
        self.pesos_indicadores = {
            # Buy Signals
            "EMA": 0.15,
            "RSI": 0.10,
            "MACD": 0.15,
            "Bollinger": 0.10,
            "Volume": 0.05,
            "ATR": 0.05,
            "LTA": 0.10,
            # Sell Signals
            "Estocastico": 0.10,
            "LTB": 0.10,
            "Pullback": 0.10
        }

    def calcular_indicadores(self):
        """
        Calcula todos os indicadores técnicos usando TA-Lib.
        """
        try:
            df = self.dados
            
            # Indicadores de Compra
            df['EMA9'] = talib.EMA(df['close'], timeperiod=9)
            df['EMA21'] = talib.EMA(df['close'], timeperiod=21)
            df['RSI'] = talib.RSI(df['close'], timeperiod=14)
            df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
            df['Bollinger_Upper'], df['Bollinger_Middle'], df['Bollinger_Lower'] = talib.BBANDS(
                df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
            )
            df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            df['LTA'] = talib.LINEARREG_ANGLE(df['close'], timeperiod=20)
            
            # Indicadores de Venda
            df['Estocastico_K'], df['Estocastico_D'] = talib.STOCH(
                df['high'], df['low'], df['close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0
            )
            df['LTB'] = talib.LINEARREG_SLOPE(df['close'], timeperiod=20)
            df['Pullback'] = talib.ROC(df['close'], timeperiod=1)
            
            return True
        except Exception as e:
            print(f"Erro ao calcular indicadores: {e}")
            return False

    def gerar_sinal(self):
        """
        Gera sinal de compra/venda com base nos indicadores calculados.
        
        :return: Tupla com as porcentagens de sinal de compra e venda.
        """
        sinal_compra = 0
        sinal_venda = 0
        
        # Lógica para Compra
        if self.dados['EMA9'].iloc[-1] > self.dados['EMA21'].iloc[-1]:
            sinal_compra += self.pesos_indicadores["EMA"] * 100
        if self.dados['RSI'].iloc[-1] < 30:
            sinal_compra += self.pesos_indicadores["RSI"] * 100
        if self.dados['MACD'].iloc[-1] > self.dados['MACD_signal'].iloc[-1]:
            sinal_compra += self.pesos_indicadores["MACD"] * 100
            
        # Lógica para Venda
        if self.dados['Estocastico_K'].iloc[-1] > 80:
            sinal_venda += self.pesos_indicadores["Estocastico"] * 100
        if self.dados['LTB'].iloc[-1] < 0:
            sinal_venda += self.pesos_indicadores["LTB"] * 100
            
        # Limitar a 100%
        sinal_compra = min(100, round(sinal_compra, 2))
        sinal_venda = min(100, round(sinal_venda, 2))
        
        return sinal_compra, sinal_venda
