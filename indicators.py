# indicators.py
import pandas as pd
import pandas_ta as ta

class Indicators:
    def __init__(self, dados):
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
        self.pesos_padroes = {
            "Hammer": 0.20,
            "Shooting Star": 0.20,
            "Bullish Engulfing": 0.20,
            "Bearish Engulfing": 0.20,
            "Doji": 0.10,
            "Marubozu": 0.10
        }

    def calcular_indicadores(self):
        """Calcula todos os indicadores técnicos."""
        try:
            df = self.dados
            
            # Indicadores de Compra
            df['EMA9'] = ta.ema(df['close'], length=9)
            df['EMA21'] = ta.ema(df['close'], length=21)
            df['RSI'] = ta.rsi(df['close'], length=14)
            df['MACD'] = ta.macd(df['close'])['MACD_12_26_9']
            df['Bollinger_Upper'], df['Bollinger_Lower'] = ta.bbands(df['close'], length=20).iloc[:, 0], ta.bbands(df['close'], length=20).iloc[:, 2]
            df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
            df['LTA'] = ta.linreg(df['close'], length=20, angle=True)
            
            # Indicadores de Venda
            df['Estocastico'] = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3)['STOCHk_14_3_3']
            df['LTB'] = ta.linreg(df['close'], length=20, slope=True)
            df['Pullback'] = ta.roc(df['close'], length=1)
            
            return True
        except Exception as e:
            print(f"Erro ao calcular indicadores: {e}")
            return False

    def detectar_padroes(self):
        """Detecta padrões de candlestick."""
        try:
            padroes = ta.cdl_pattern(
                self.dados['open'], self.dados['high'], 
                self.dados['low'], self.dados['close'],
                name=["hammer", "shootingstar", "engulfing", "doji", "marubozu"]
            )
            
            # Mapear padrões detectados
            for idx, row in padroes.iloc[-5:].iterrows():  # Últimas 5 velas
                for padrao, valor in row.items():
                    if valor != 0:
                        acao = "Comprar" if valor > 0 else "Vender"
                        self.padroes_detectados.append({
                            "timestamp": self.dados.iloc[idx]['timestamp'],
                            "padrao": padrao.split('_')[-1].capitalize(),
                            "acao": acao
                        })
            return True
        except Exception as e:
            print(f"Erro ao detectar padrões: {e}")
            return False

    def gerar_sinal(self):
        """Gera sinal de compra/venda com base nos indicadores e padrões."""
        sinal_compra = 0
        sinal_venda = 0
        
        # Lógica para Compra
        if self.dados['EMA9'].iloc[-1] > self.dados['EMA21'].iloc[-1]:
            sinal_compra += self.pesos_indicadores["EMA"] * 100
        if self.dados['RSI'].iloc[-1] < 30:
            sinal_compra += self.pesos_indicadores["RSI"] * 100
            
        # Lógica para Venda
        if self.dados['Estocastico'].iloc[-1] > 80:
            sinal_venda += self.pesos_indicadores["Estocastico"] * 100
            
        # Limitar a 100%
        sinal_compra = min(100, round(sinal_compra, 2))
        sinal_venda = min(100, round(sinal_venda, 2))
        
        return sinal_compra, sinal_venda

    def obter_padroes_recentes(self):
        """Retorna os últimos padrões detectados formatados."""
        return [
            f"- {p['padrao']} ({p['timestamp']}) - {p['acao']} {self.pesos_padroes.get(p['padrao'], 0)*100}%"
            for p in self.padroes_detectados[-2:]  # Últimos 2 padrões
        ]
