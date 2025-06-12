from flask import Flask, render_template_string, request
from alerta import enviar_alerta
import os  # Necesario para leer la variable de entorno PORT

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Alerta Trading</title>
</head>
<body style="font-family: Arial; text-align: center; margin-top: 50px;">
    <h1>🚀 Alerta de Trading</h1>
    <form method="POST">
        <button type="submit" style="font-size: 20px; padding: 10px 30px;">Enviar Alerta</button>
    </form>
    {% if resultado %}
        <p style="margin-top: 20px;"><strong>{{ resultado }}</strong></p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = ""
    if request.method == "POST":
        resultado = enviar_alerta()
    return render_template_string(HTML_TEMPLATE, resultado=resultado)

if __name__ == "__main__":
    # Render define el puerto en la variable de entorno PORT
    port = int(os.environ.get("PORT", 10000))  # 10000 para correr localmente si PORT no existe
    app.run(host='0.0.0.0', port=port)
# redeploy trigger
