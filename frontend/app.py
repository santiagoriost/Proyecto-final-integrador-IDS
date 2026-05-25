from flask import Flask
from cafeteria_web.routes.inicio import inicio_bp
from cafeteria_web.routes.login import login_bp
app = Flask(__name__)

app.config["SECRET_KEY"] = "despues_vemos_que_pongo"

app.register_blueprint(inicio_bp)
app.register_blueprint(login_bp, url_prefix="/login")

if __name__ == "__main__":
    app.run(port=5002, debug=True)