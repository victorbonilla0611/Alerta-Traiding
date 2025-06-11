from flask import Flask
from alerta import enviar_alerta

app = Flask(__name__)

@app.route('/')
def inicio():
    return enviar_alerta()

app.run(host='0.0.0.0', port=81)
