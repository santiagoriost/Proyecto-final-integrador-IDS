from flask import Flask
from cafeteria_web.routes.inicio import inicio_bp
app = Flask(__name__)

app.register_blueprint(inicio_bp, url_prefix="/inicio")

if __name__ == "__main__":
    app.run(port=5002, debug=True)