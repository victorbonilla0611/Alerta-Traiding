import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from newsapi import NewsApiClient
import os
import requests
import datetime

def enviar_telegram(mensaje):
    bot_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": mensaje}
    response = requests.post(url, data=data)
    return response.json()

def enviar_alerta():
    activos = ["AAPL", "TSLA", "AMZN", "MSFT", "GOOGL", "META", "NFLX", "BTC-USD", "GC=F", "CL=F"]

    api_key = os.getenv("NEWS_API_KEY")
    newsapi = NewsApiClient(api_key=api_key)

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

        desde = (datetime.datetime.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
        noticias = newsapi.get_everything(q=ticker, from_param=desde, sort_by="relevancy", language="en", page_size=1)
        titular = noticias["articles"][0]["title"] if noticias["articles"] else "Sin noticias"

        mensaje = f"""
📈 ALERTA DE TRADING ({ticker}) [15 min]
Precio actual: {precio:.2f}
RSI: {rsi:.2f}
Señal próximos 30 min: {señal}
📰 {titular}
"""
        if señal != "⏸️ ESPERAR":
            mensajes.append(mensaje)

    for msg in mensajes:
        enviar_telegram(msg)

    return "✅ Alerta enviada con éxito." if mensajes else "⏸️ No hubo señales de compra o venta claras."
