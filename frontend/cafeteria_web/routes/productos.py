from flask import Blueprint, request, jsonify, render_template
import requests
API_URL = "http://localhost:5001/productos"
productos_bp = Blueprint("productos", __name__)

@productos_bp.route("/productos", methods=["GET"])
def pagina_productos():
    try:
        limit = request.args.get("_limit", 10)
        offset = request.args.get("_offset", 0)
        url = f"{API_URL}?_limit={limit}&_offset={offset}"
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            lista_productos = datos.get("productos", [])
            links_hateos = datos.get("_links", {})
            return render_template('productos.html', productos = lista_productos, links = links_hateos)
    except Exception as e:
        return render_template('productos.html')
