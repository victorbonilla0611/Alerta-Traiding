import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import datetime
import os
import requests

def enviar_alerta():
    activos = ["AAPL", "TSLA", "AMZN", "MSFT", "GOOGL", "META", "NFLX", "NVDA", "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "AUDUSD=X", "GBPJPY=X", "USDCHF=X", "NZDUSD=X", "EURJPY=X", "^NDX", "SI=F", "GC=F", "CL=F"]


    noticias_api_key = os.getenv("NEWS_API_KEY")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    mensajes = []

    for ticker in activos:
        df = yf.download(ticker, interval="15m", period="1d")
        if df.empty or len(df) < 30:
            continue

        df["MA20"] = df["Close"].rolling(20).mean()
        df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(14).mean()))
        df.dropna(inplace=True)

        if len(df) < 3:
            continue

        df["Target"] = (df["Close"].shift(-2) > df["Close"]).astype(int)

        X = df[["Close", "MA20", "RSI"]]
        y = df["Target"]

        model = RandomForestClassifier()
        model.fit(X[:-2], y[:-2])
        pred = model.predict(X[-1:])[0]
        rsi = df["RSI"].iloc[-1]
        precio = float(df["Close"].iloc[-1])

        if rsi < 45 and pred == 1:
            señal = "💰 COMPRA"
        elif rsi > 60 and pred == 0:
            señal = "⚠️ VENTA"
        else:
            señal = "⏸️ ESPERAR"

        # Noticias
        titular = "Sin noticias relevantes"
        try:
            import requests
            fecha = (datetime.datetime.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
            url = f"https://newsapi.org/v2/everything?q={ticker}&from={fecha}&sortBy=relevancy&language=en&pageSize=1&apiKey={noticias_api_key}"
            res = requests.get(url).json()
            if res.get("articles"):
                titular = res["articles"][0]["title"]
        except Exception as e:
            titular = "Error al obtener noticias"

        if señal != "⏸️ ESPERAR":
            mensaje = f"""
📈 ALERTA DE TRADING ({ticker}) [15 min]
Precio actual: ${precio:.2f}
RSI: {rsi:.2f}
Señal próximos 30 min: {señal}
📰 {titular}
"""
            mensajes.append(mensaje)

    if mensajes:
        for msg in mensajes:
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            data = {"chat_id": chat_id, "text": msg}
            requests.post(url, data=data)
        return "✅ Alerta(s) enviada(s) por Telegram"
    else:
        return "⏸️ No hubo señales de compra o venta claras"
