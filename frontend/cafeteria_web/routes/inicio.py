from flask import Blueprint, request, jsonify, render_template

inicio_bp = Blueprint("inicio", __name__)

@inicio_bp.route("/", methods=["GET"])
def pagina_inicio():
    return render_template("inicio.html")