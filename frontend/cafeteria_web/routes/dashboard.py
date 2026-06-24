from flask import request, Blueprint, render_template, flash, url_for, redirect, session
import os
from werkzeug.utils import secure_filename
import requests
BACK_APP_HOST = os.environ.get("BACK_APP_HOST")
API_URL_PRODUCTOS = f"http://{BACK_APP_HOST}:5001/productos"
API_RESERVAS_URL = f"http://{BACK_APP_HOST}:5001/reservas"
API_HISTORIAL_URL = f"http://{BACK_APP_HOST}:5001/historial"
UPLOAD_FOLDER = '/app/static/imagenes/foto_productos'
EXTENSIONES_PERMITIDAS = {'.png', '.jpg', '.jpeg', '.webp'}

dashboard_bp = Blueprint("dashboard", __name__)
@dashboard_bp.before_request
def proteger_rutas_admin():
    if not session.get("token"):
        flash("Debes iniciar sesión para acceder al panel admin.", "error")
        return redirect(url_for("usuarios.manejo_login"))

    if session.get("rol") != "admin":
        flash("No tienes permisos para acceder al panel admin.", "error")
        return redirect(url_for("inicio.pagina_inicio"))
    
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
        url = f"{API_URL_PRODUCTOS}?_limit={limit}&_offset={offset}"
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
    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    if request.method == "POST":
        img = request.files.get("fproducto_img")
        ruta_imagen_db = None
        if img and img.filename != "":
            nombre_seguro = secure_filename(img.filename)
            extension = os.path.splitext(nombre_seguro)[1].lower()

            if extension not in EXTENSIONES_PERMITIDAS:
                flash("Formato de imagen no permitido. Usar PNG, JPG, JPEG, WEBP", "error")
                return redirect(request.url)

            nuevo_nombre = f"producto_id_{id_producto}{extension}"
            filepath = os.path.join(UPLOAD_FOLDER, nuevo_nombre)
            
            os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
            for archivo in os.listdir(UPLOAD_FOLDER):
                if archivo.startswith(f"producto_id_{id_producto}") or archivo.startswith(f"producto_id_{id_producto}."):
                    try:
                        os.remove(os.path.join(UPLOAD_FOLDER, archivo))
                    except Exception:
                        pass
        
            img.save(filepath)
            ruta_imagen_db = f"imagenes/foto_productos/{nuevo_nombre}"

        datos = {
            "nombre": request.form.get("fproducto_nombre", "").strip(),
            "precio": request.form.get("fproducto_precio", "").strip(),
            "stock": request.form.get("fproducto_stock", "").strip(),
            "tipo": request.form.get("fproducto_tipo", "").strip(),
            "local_producto": request.form.get("fproducto_local_id", "").strip(),
            "descripcion": request.form.get("fproducto_desc", "").strip(),
        }
        if ruta_imagen_db:
            datos["imagen"] = ruta_imagen_db
        try:
            respuesta = requests.patch(f"{API_URL_PRODUCTOS}/{id_producto}", json=datos, headers=headers)
            if respuesta.status_code == 200:
                flash("Producto modificado correctamente", "success")
                return redirect(url_for('dashboard.dashboard_productos'))
            else:
                datos_error = respuesta.json()
                flash(f"No se pudo modificar: {datos_error}", "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    respuesta = requests.get(f"{API_URL_PRODUCTOS}/{id_producto}", headers=headers)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return render_template("dashboard_producto_BM.html", producto=datos)
    flash("Producto no encontrado", "error")
    return redirect(url_for("dashboard.dashboard_productos"))

@dashboard_bp.route("/producto/<int:id_producto>/eliminar", methods=["POST"])
def eliminar_producto(id_producto):
    token = session.get("token")
    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    img = None
    try:
        datos_request = requests.get(f"{API_URL_PRODUCTOS}/{id_producto}", headers=headers)
        if datos_request.status_code == 200:
            datos_producto = datos_request.json()
            img = datos_producto.get("imagen")
    except Exception as e:
        flash(f"error: {str(e)}", "error")
    try:
        respuesta = requests.delete(f"{API_URL_PRODUCTOS}/{id_producto}", headers=headers)
        if respuesta.status_code == 200:
            if img:
                filename = os.path.basename(img)
                ruta_img = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.exists(ruta_img):
                    try:
                        os.remove(ruta_img)
                    except Exception as e:
                        flash(f"Producto eliminado pero no se pudo eliminar la imagen: {str(e)}", "error")
            flash("Producto eliminado correctamente", "success")
            return redirect(url_for('dashboard.dashboard_productos'))
        flash("No se pudo eliminar el producto", "error")
    except Exception as e:
        flash(f"error: {str(e)}", "error")
    return redirect(url_for('dashboard.dashboard_productos'))

@dashboard_bp.route("/producto", methods=["GET", "POST"])
def agregar_producto():
    token = session.get("token")
    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}
    if request.method == "POST":
        img = request.files.get("fproducto_img")
        
        if img and img.filename != "":
            nombre_seguro = secure_filename(img.filename)
            extension = os.path.splitext(nombre_seguro)[1].lower()
            if extension not in EXTENSIONES_PERMITIDAS:
                flash("Formato de imagen no permitido. Usar PNG, JPG, JPEG, WEBP", "error")
                return redirect(request.url)
        else:
            extension = None
        
        datos = {
            "nombre": request.form.get("fproducto_nombre", "").strip(),
            "precio": request.form.get("fproducto_precio", "").strip(),
            "stock": request.form.get("fproducto_stock", "").strip(),
            "tipo": request.form.get("fproducto_tipo", "").strip(),
            "local_producto": request.form.get("fproducto_local_id", "").strip(),
            "descripcion": request.form.get("fproducto_desc", "").strip(),
            "imagen": None
        }
        try:
            respuesta = requests.post(API_URL_PRODUCTOS, json=datos, headers=headers)
            if respuesta.status_code == 200:
                producto = respuesta.json()
                id = producto.get("id")

                if img and extension:
                    nuevo_nombre = f"producto_id_{id}{extension}"
                    filepath = os.path.join(UPLOAD_FOLDER, nuevo_nombre)

                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    img.save(filepath)
                    ruta_imagen_db = f"imagenes/foto_productos/{nuevo_nombre}"

                    patch_resp = requests.patch(f"{API_URL_PRODUCTOS}/{id}", json={"imagen": ruta_imagen_db}, headers=headers)
                    if patch_resp.status_code != 200:
                        flash(f"Producto creado pero la imagen no se guardó: {patch_resp.json()}", "error")
                        return redirect(url_for('dashboard.dashboard_productos'))
                    
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
@dashboard_bp.route("/admin/reservas/<int:id_reserva>/estado", methods=["POST"])
def cambiar_estado_reserva(id_reserva):
    estado = request.form.get("estado")
    datos = {
        "estado": estado
    }
    try:
        respuesta = requests.patch(
            f"{API_RESERVAS_URL}/{id_reserva}/estado",
            json=datos
        )
        if respuesta.status_code == 200:
            registrar_accion(
                "Estado de reserva actualizado",
                "reserva",
                f"Reserva #{id_reserva} cambió a estado {estado}"
            )
            flash("Estado actualizado ", "success")
        else:
            flash("No se pudo actualizar", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_reservas"))

@dashboard_bp.route("/admin/reservas/<int:id_reserva>/eliminar", methods=["POST"])
def eliminar_reserva_admin(id_reserva):
    try:
        respuesta = requests.delete(
            f"{API_RESERVAS_URL}/{id_reserva}"
        )
        if respuesta.status_code == 200:
            flash("Reserva eliminada correctamente", "success")
        else:
            datos_error = respuesta.json()
            flash(
                datos_error.get("error", "No se pudo eliminar la reserva"),
                "error"
            )
    except Exception as e:
        flash(f"Error al eliminar reserva: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_reservas"))

@dashboard_bp.route("/admin/reservas/crear", methods=["POST"])
def crear_reserva_admin():
    datos = {
        "nombre_cliente": request.form.get("nombre_cliente", "").strip(),
        "correo_cliente": request.form.get("correo_cliente", "").strip(),
        "tipo_reserva": request.form.get("tipo_reserva", "").strip(),
        "fecha_reserva": request.form.get("fecha_reserva", "").strip(),
        "hora_reserva": request.form.get("hora_reserva", "").strip(),
        "numero_personas": request.form.get("numero_personas", "").strip(),
        "comentarios": request.form.get("comentarios", "").strip()
    }
    try:
        respuesta = requests.post(
            f"{API_RESERVAS_URL}/",
            json=datos
        )
        if respuesta.status_code == 201:
            flash("Reserva creada correctamente", "success")
        else:
            datos_error = respuesta.json()
            flash(
                datos_error.get("error", "No se pudo crear la reserva"),
                "error"
            )
    except Exception as e:
        flash(f"Error al crear reserva: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_reservas"))

@dashboard_bp.route("/admin/reservas/validar", methods=["POST"])
def validar_reserva_admin():
    codigo_reserva = request.form.get("codigo_reserva", "").strip()
    if codigo_reserva == "":
        flash("Debes ingresar un código de reserva", "error")
        return redirect(url_for("dashboard.dashboard_reservas"))
    try:
        respuesta = requests.patch(
            f"{API_RESERVAS_URL}/validar",
            json={"codigo_reserva": codigo_reserva}
        )
        datos = respuesta.json()
        if respuesta.status_code == 200:
            reserva = datos.get("reserva", {})
            flash(
                f"Reserva validada correctamente: {reserva.get('nombre_cliente')}",
                "success"
            )
        else:
            flash(datos.get("error", "No se pudo validar la reserva"), "error")
    except Exception as e:
        flash(f"Error al validar reserva: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_reservas"))

@dashboard_bp.route("/admin/ventas", methods=["GET"])
def dashboard_ventas():
    productos = []
    ventas = []
    detalles_ventas = {}
    try:
        respuesta_productos = requests.get(API_URL_PRODUCTOS)
        if respuesta_productos.status_code == 200:
            datos_productos = respuesta_productos.json()
            productos = datos_productos.get("productos", [])
        respuesta_ventas = requests.get(f"http://{BACK_APP_HOST}:5001/ventas/")
        if respuesta_ventas.status_code == 200:
            datos_ventas = respuesta_ventas.json()
            ventas = datos_ventas.get("ventas", [])
            for venta in ventas:
                respuesta_detalle = requests.get(
                    f"http://{BACK_APP_HOST}:5001/ventas/{venta['id_venta']}"
                )

                if respuesta_detalle.status_code == 200:
                    detalles_ventas[venta["id_venta"]] = (
                        respuesta_detalle.json().get("detalles", [])
                    )

    except Exception as e:
        print(e)
    return render_template(
    "dashboard_ventas.html",
    productos=productos,
    ventas=ventas,
    detalles_ventas=detalles_ventas
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
            f"http://{BACK_APP_HOST}:5001/ventas/",
            json=datos
        )
        if respuesta.status_code == 201:
            registrar_accion(
                "Venta registrada",
                "venta",
                f"Se registró una venta del producto ID {producto_id} por cantidad {cantidad}"
            )
            flash("venta registrada", "success")
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
    mas_vendidos = []
    try:
        respuesta_reservas = requests.get(
            f"{API_RESERVAS_URL}/?limit=100"
        )
        if respuesta_reservas.status_code == 200:
            datos_reservas = respuesta_reservas.json()
            reservas = datos_reservas.get("reservas", [])

        respuesta_mas_vendidos = requests.get(
            f"http://{BACK_APP_HOST}:5001/ventas/mas-vendidos"
        )
        if respuesta_mas_vendidos.status_code == 200:
            datos_mas_vendidos = respuesta_mas_vendidos.json()
            mas_vendidos = datos_mas_vendidos.get("mas_vendidos", [])

        respuesta_ventas = requests.get(
            f"http://{BACK_APP_HOST}:5001/ventas/"
        )
        if respuesta_ventas.status_code == 200:
            datos_ventas = respuesta_ventas.json()
            ventas = datos_ventas.get("ventas", [])
    except Exception as e:
        print(e)
    return render_template(
        "dashboard_estadisticas.html",
        reservas=reservas,
        ventas=ventas,
        mas_vendidos=mas_vendidos
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

@dashboard_bp.route("/admin/mas-vendidos", methods=["GET"])
def dashboard_mas_vendidos():
    mas_vendidos = []
    try:
        respuesta = requests.get(f"http://{BACK_APP_HOST}:5001/ventas/mas-vendidos")
        if respuesta.status_code == 200:
            mas_vendidos = respuesta.json().get("mas_vendidos", [])
    except Exception as e:
        print(e)
    return render_template(
        "dashboard_mas_vendidos.html",
        mas_vendidos=mas_vendidos
    )

@dashboard_bp.route("/admin/resenas")
def dashboard_resenas():
    token = session.get("token")

    if not token:
        flash("Debes iniciar sesión", "error")
        return redirect(url_for("usuarios.manejo_login"))
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        respuesta = requests.get(
            f"http://{BACK_APP_HOST}:5001/resenas/",
            headers=headers
        )
        if respuesta.status_code != 200:
            flash(
                "No se pudieron obtener las reseñas",
                "error"
            )
            return render_template(
                "dashboard_resenas.html",
                resenas=[]
            )
        datos = respuesta.json()
        return render_template(
            "dashboard_resenas.html",
            resenas=datos.get("reseñas", [])
        )
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return render_template(
            "dashboard_resenas.html",
            resenas=[]
        )
@dashboard_bp.route("/admin/resenas/<int:id_resena>/eliminar", methods=["POST"])
def eliminar_resena_admin(id_resena):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        respuesta = requests.delete(
            f"http://{BACK_APP_HOST}:5001/resenas/{id_resena}",
            headers=headers
        )
        if respuesta.status_code == 200:
            flash("Reseña eliminada correctamente", "success")
        else:
            flash("No se pudo eliminar la reseña", "error")
        return redirect(url_for("dashboard.dashboard_resenas"))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_resenas"))

@dashboard_bp.route("/admin/resenas/<int:id_resena>/responder", methods=["POST"])
def responder_resena_admin(id_resena):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    respuesta_texto = request.form.get("respuesta", "").strip()
    try:
        resp = requests.patch(
            f"http://{BACK_APP_HOST}:5001/resenas/{id_resena}/respuesta",
            json={"respuesta": respuesta_texto},
            headers=headers
        )
        if resp.status_code == 200:
            flash("Respuesta guardada correctamente", "success")
        else:
            flash("No se pudo guardar la respuesta", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_resenas"))