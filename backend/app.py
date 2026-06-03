from flask import Flask, blueprints
from flask_jwt_extended import JWTManager
from routes.productos import productos_bp
from routes.usuarios import usuarios_bp
from routes.admin import administradores_bp
from routes.reservas import reservas_bp
from routes.reseñas import reseñas_bp 
from routes.locales import locales_bp  
from extensions import mail
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True

app.config["MAIL_USERNAME"] = "jcunduri@fi.uba.ar"
app.config["MAIL_PASSWORD"] = "iozymlankfcbasbk"
app.config["SECRET_KEY"] = "despues_vemos_que_pongo"
jwt = JWTManager(app)
mail.init_app(app)

app.register_blueprint(productos_bp, url_prefix="/productos")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
app.register_blueprint(administradores_bp, url_prefix="/administradores")
app.register_blueprint(reseñas_bp, url_prefix="/reseñas")
app.register_blueprint(reservas_bp, url_prefix="/reservas")
app.register_blueprint(locales_bp, url_prefix="/locales")

if __name__ == "__main__":
    app.run(port=5001, debug=True)