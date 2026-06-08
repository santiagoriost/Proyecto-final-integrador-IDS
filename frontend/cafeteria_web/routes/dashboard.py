from flask import request, Blueprint, render_template, flash, url_for, redirect, session
import requests
API_URL = "http://localhost:5001/productos"
API_RESERVAS_URL = "http://localhost:5001/reservas"
API_HISTORIAL_URL = "http://localhost:5001/historial"
dashboard_bp = Blueprint("dashboard", __name__)
def registrar_accion(accion, tipo, detalle=""):
    try:
        requests.post(
            f"{API_HISTORIAL_URL}/",
            json={"accion": accion, "tipo": tipo, "detalle": detalle}
        )
    except Exception as e:
        print(f"Error registrando acción: {e}")

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
            return render_template(
                "dashboard_productos.html",
                productos=lista_productos,
                links=links_hateos
            )
        flash("No se pudieron cargar los productos", "error")
        return render_template(
            "dashboard_productos.html",
            productos=[],
            links={}
        )
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return render_template(
            "dashboard_productos.html",
            productos=[],
            links={}
        )
@dashboard_bp.route("/producto/<int:id_producto>", methods=["GET", "POST"])
def gestionar_producto(id_producto):
    token = session.get("token")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    if request.method == "POST":
        datos = {
            "nombre": request.form.get("fproducto_nombre", "").strip(),
            "precio": request.form.get("fproducto_precio", "").strip(),
            "stock": request.form.get("fproducto_stock", "").strip(),
            "tipo": request.form.get("fproducto_tipo", "").strip(),
            "local_producto": request.form.get("fproducto_local_id", "").strip()
        }
        try:
            respuesta = requests.patch(f"{API_URL}/{id_producto}", json=datos, headers=headers)
            if respuesta.status_code == 200:
                flash("Producto modificado correctamente", "success")
                return redirect(url_for('dashboard.dashboard_productos'))
            else:
                datos_error = respuesta.json()
                flash(f"No se pudo modificar: {datos_error}", "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    respuesta = requests.get(f"{API_URL}/{id_producto}", headers=headers)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return render_template("dashboard_producto_BM.html", producto=datos)
    flash("Producto no encontrado", "error")
    return redirect(url_for("dashboard.dashboard_productos"))

@dashboard_bp.route("/producto/<int:id_producto>/eliminar", methods=["POST"])
def eliminar_producto(id_producto):
    token = session.get("token")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    try:
        respuesta = requests.delete(f"{API_URL}/{id_producto}", headers=headers)
        if respuesta.status_code == 200:
            flash("Producto eliminado correctamente", "success")
            return redirect(url_for('dashboard.dashboard_productos'))
        flash("No se pudo eliminar el producto", "error")
    except Exception as e:
        flash(f"error: {str(e)}", "error")
    return redirect(url_for('dashboard.dashboard_productos'))

@dashboard_bp.route("/producto", methods=["GET", "POST"])
def agregar_producto():
    token = session.get("token")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    if request.method == "POST":
        datos = {
            "nombre": request.form.get("fproducto_nombre", "").strip(),
            "precio": request.form.get("fproducto_precio", "").strip(),
            "stock": request.form.get("fproducto_stock", "").strip(),
            "tipo": request.form.get("fproducto_tipo", "").strip(),
            "local_producto": request.form.get("fproducto_local_id", "").strip()
        }
        try:
            respuesta = requests.post(API_URL, json=datos, headers=headers)
            if respuesta.status_code == 200:
                flash("Producto agregado correctamente", "success")
                return redirect(url_for('dashboard.dashboard_productos'))
            else:
                datos_error = respuesta.json()
                flash(f"No se pudo agregar el producto: {datos_error}", "error")
        except Exception as e:
            flash(f"Error en el backend: {str(e)}", "error")
    return render_template('dashboard_producto_altas.html')

@dashboard_bp.route("/admin/reservas", methods=["GET"])
def dashboard_reservas():
    try:
        limit = request.args.get("limit", 10)
        offset = request.args.get("offset", 0)
        url = f"{API_RESERVAS_URL}/?limit={limit}&offset={offset}"
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            lista_reservas = datos.get("reservas", [])
            links_hateos = datos.get("_links", {})
            return render_template(
                "dashboard_reservas.html",
                reservas=lista_reservas,
                links=links_hateos
            )
        flash("No se pudieron cargar las reservas", "error")
        return render_template(
            "dashboard_reservas.html",
            reservas=[],
            links={}
        )
    except Exception as e:
        flash(f"Error al cargar reservas: {str(e)}", "error")
        return render_template(
            "dashboard_reservas.html",
            reservas=[],
            links={}
        )
@dashboard_bp.route(
    "/admin/reservas/<int:id_reserva>/estado",
    methods=["POST"]
)
def cambiar_estado_reserva(id_reserva):
    estado = request.form.get("estado")
    datos = {
        "estado": estado
    }
    try:
        respuesta = requests.patch(
            f"http://127.0.0.1:5001/reservas/{id_reserva}/estado",
            json=datos
        )
        if respuesta.status_code == 200:
            flash("Estado actualizado 😎", "success")
        else:
            flash("No se pudo actualizar", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_reservas"))

@dashboard_bp.route("/admin/ventas", methods=["GET"])
def dashboard_ventas():
    productos = []
    ventas = []
    try:
        respuesta_productos = requests.get("http://127.0.0.1:5001/productos/")
        if respuesta_productos.status_code == 200:
            datos_productos = respuesta_productos.json()
            productos = datos_productos.get("productos", [])
        respuesta_ventas = requests.get("http://127.0.0.1:5001/ventas/")
        if respuesta_ventas.status_code == 200:
            datos_ventas = respuesta_ventas.json()
            ventas = datos_ventas.get("ventas", [])
    except Exception as e:
        print(e)
    return render_template(
        "dashboard_ventas.html",
        productos=productos,
        ventas=ventas
    )

@dashboard_bp.route(
    "/admin/ventas/registrar",
    methods=["POST"]
)
def registrar_venta_admin():
    producto_id = request.form.get("producto_id")
    cantidad = request.form.get("cantidad")
    datos = {
        "productos": [
            {
                "producto_id": int(producto_id),
                "cantidad": int(cantidad)
            }
        ]
    }
    try:
        respuesta = requests.post(
            "http://127.0.0.1:5001/ventas/",
            json=datos
        )
        if respuesta.status_code == 201:
            flash("Venta registrada 😎", "success")
        else:
            datos_error = respuesta.json()
            flash(
                datos_error.get(
                    "error",
                    "No se pudo registrar"
                ),
                "error"
            )
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    return redirect(
        url_for("dashboard.dashboard_ventas")
    )

@dashboard_bp.route("/estadisticas", methods=["GET"])
def dashboard_estadisticas():
    reservas = []
    ventas = []
    try:
        respuesta_reservas = requests.get(
            "http://127.0.0.1:5001/reservas/?limit=100"
        )
        if respuesta_reservas.status_code == 200:
            datos_reservas = respuesta_reservas.json()
            reservas = datos_reservas.get("reservas", [])
        respuesta_ventas = requests.get(
            "http://127.0.0.1:5001/ventas/"
        )
        if respuesta_ventas.status_code == 200:
            datos_ventas = respuesta_ventas.json()
            ventas = datos_ventas.get("ventas", [])
    except Exception as e:
        print(e)
    return render_template(
        "dashboard_estadisticas.html",
        reservas=reservas,
        ventas=ventas
    )
@dashboard_bp.route("/admin/reportes", methods=["GET"])
def dashboard_reportes():
    reservas = []
    ventas = []
    productos = []
    try:
        respuesta_reservas = requests.get("http://127.0.0.1:5001/reservas/?limit=100")
        if respuesta_reservas.status_code == 200:
            reservas = respuesta_reservas.json().get("reservas", [])

        respuesta_ventas = requests.get("http://127.0.0.1:5001/ventas/")
        if respuesta_ventas.status_code == 200:
            ventas = respuesta_ventas.json().get("ventas", [])

        respuesta_productos = requests.get("http://127.0.0.1:5001/productos/")
        if respuesta_productos.status_code == 200:
            productos = respuesta_productos.json().get("productos", [])
    except Exception as e:
        print(e)
    return render_template(
        "dashboard_reportes.html",
        reservas=reservas,
        ventas=ventas,
        productos=productos
    )
@dashboard_bp.route("/admin/historial", methods=["GET"])
def dashboard_historial():
    historial = []
    try:
        respuesta = requests.get(f"{API_HISTORIAL_URL}/")
        if respuesta.status_code == 200:
            historial = respuesta.json().get("historial", [])
    except Exception as e:
        print(e)
    return render_template("dashboard_historial.html", historial=historial)