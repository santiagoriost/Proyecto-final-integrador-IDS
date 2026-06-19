from flask import Flask
from cafeteria_web.routes.inicio import inicio_bp
from cafeteria_web.routes.usuarios import usuarios_bp
from cafeteria_web.routes.dashboard import dashboard_bp
from cafeteria_web.routes.ubicacion import ubicacion_bp
from cafeteria_web.routes.carrito import carrito_bp
from cafeteria_web.routes.resenas import resenas_bp
app = Flask(__name__)

app.config["SECRET_KEY"] = "despues_vemos_que_pongo"

app.register_blueprint(inicio_bp)
app.register_blueprint(usuarios_bp, url_prefix="/usuario")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(ubicacion_bp, url_prefix="/ubicacion")
app.register_blueprint(carrito_bp, url_prefix="/carrito")
app.register_blueprint(resenas_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)