from flask import Blueprint, request, jsonify, render_template
import requests
inicio_bp = Blueprint("inicio", __name__)

@inicio_bp.route("/", methods=["GET"])
def pagina_inicio():
    return render_template("inicio.html")

@inicio_bp.route("/reservas", methods=["GET"])
def pagina_reservas():
    return render_template("reservas.html")

    