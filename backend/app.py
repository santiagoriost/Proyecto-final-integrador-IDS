from flask import Flask, blueprints
from routes.productos import productos_bp
from routes.usuarios import usuarios_bp
from routes.admin import administradores_bp
from routes.reservas import reservas_bp

app = Flask(__name__)

app.register_blueprint(productos_bp, url_prefix="/productos")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
app.register_blueprint(administradores_bp, url_prefix="/administradores")
app.register_blueprint(reservas_bp, url_prefix="/reservas")

if __name__ == "__main__":
    app.run(port=5001, debug=True)