from flask import Flask
from alerta import enviar_alerta

app = Flask(__name__)

@app.route('/')
def index():
    return enviar_alerta()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
