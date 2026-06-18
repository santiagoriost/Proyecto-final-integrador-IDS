from flask import Flask, blueprints,jsonify
from flask_jwt_extended import JWTManager
from routes.productos import productos_bp
from routes.usuarios import usuarios_bp
from routes.admin import administradores_bp
from routes.reservas import reservas_bp
from routes.resenas import resenas_bp 
from routes.locales import locales_bp 
from routes.carrito import carrito_bp 
from extensions import mail
from flask_cors import CORS
from routes.ventas import ventas_bp
from routes.historial import historial_bp
from datetime import timedelta

app = Flask(__name__)
CORS(app)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_DEBUG"] = True

app.config["MAIL_USERNAME"] = "jcunduri@fi.uba.ar"
app.config["MAIL_PASSWORD"] = "iozymlankfcbasbk"
app.config["SECRET_KEY"] = "despues_vemos_que_pongo"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)
mail.init_app(app)

@jwt.unauthorized_loader
def unauthorized_callback(msg):
    print ("JWT UNAUTHORIZED", msg)
    return jsonify({"error": msg}), 401

@jwt.invalid_token_loader
def invalid_token_callback(msg):
    print ("JWT INVALID", msg)
    return jsonify({"error": msg}), 401

app.register_blueprint(productos_bp, url_prefix="/productos")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
app.register_blueprint(administradores_bp, url_prefix="/administradores")
app.register_blueprint(resenas_bp, url_prefix="/reseñas")
app.register_blueprint(reservas_bp, url_prefix="/reservas")
app.register_blueprint(locales_bp, url_prefix="/locales")
app.register_blueprint(ventas_bp, url_prefix="/ventas")
app.register_blueprint(carrito_bp, url_prefix="/api/carrito")
app.register_blueprint(historial_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)