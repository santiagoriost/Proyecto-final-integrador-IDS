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

@dashboard_bp.route("/producto/<int:id_producto>/", methods=["GET", "POST"])
def gestionar_producto(id_producto):
    if request.method == "POST":
        nombre = request.form.get("fproducto_nombre", "").strip()
        precio = request.form.get("fproducto_precio", "").strip()
        stock = request.form.get("fproducto_stock", "").strip()
        tipo = request.form.get("fproducto_tipo", "").strip()
        local = request.form.get("fproducto_local", "").strip()
        datos = {
            "nombre": nombre,
            "precio": precio,
            "stock": stock,
            "tipo": tipo,
            "local": local
        }
        try:
            respuesta = requests.patch(f"{API_URL}/{id_producto}", json=datos)
            if respuesta.status_code == 200:
                flash("Producto modificado correctamente", "success")
                return redirect(url_for('dashboard.dashboard_productos'))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    respuesta = requests.get(f"{API_URL}/{id_producto}")
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return render_template("dashboard_producto_BM.html", producto=datos)
    flash("Producto no encontrado", "error")
    return redirect(url_for("dashboard.dashboard_productos"))

@dashboard_bp.route("/producto/<int:id_producto>/eliminar", methods=["POST"])
def eliminar_producto(id_producto):
    try:
        response = requests.delete(f"{API_URL}/{id_producto}")
        if response.status_code == 200:
            flash("Producto eliminado correctamente", "success")
            return redirect(url_for('dashboard.dashboard_productos'))
        flash("No se pudo eliminar el producto", "error")
    except Exception as e:
        flash(f"error: {str(e)}", "error")
    return redirect(url_for('dashboard.dashboard_productos'))