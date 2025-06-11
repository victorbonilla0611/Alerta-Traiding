from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from alerta import enviar_alerta

app = Flask(__name__)

@app.route("/")
def index():
    resultado = enviar_alerta()
    return resultado

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
