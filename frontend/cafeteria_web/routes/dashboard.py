from flask import request, Blueprint, render_template, flash, url_for, redirect
import requests
API_URL = "http://localhost:5001/productos"

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/productos/", methods=["GET"])
def dashboard_productos():
    try:
        limit = request.args.get("_limit", 10)
        offset = request.args.get("_offset", 0)
        url = f"{API_URL}?_limit={limit}&_offset={offset}"
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            lista_productos = datos.get("productos", [])
            links_hateos = datos.get("_links", {})
            return render_template('dashboard_productos.html', productos = lista_productos, links = links_hateos)
    except Exception as e:
        flash('Datos no encontrados', 'error')
        return render_template('dashboard_productos.html')
    