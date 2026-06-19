
from flask import (Blueprint, render_template, redirect, url_for, flash, session, request)
import requests
import os
carrito_bp = Blueprint("carrito",__name__)
BACK_APP_HOST = os.environ.get("BACK_APP_HOST", "backend_app")
API_CARRITO = f"http://{BACK_APP_HOST}:5001/api/carrito"


@carrito_bp.route("/", methods=["GET"])
def mostrar_carrito():

    token = session.get("token")

    if not token:
        flash("Debes iniciar sesión","error")
        return redirect(url_for("usuarios.manejo_login"))

    try:

        headers = {"Authorization":f"Bearer {token}"}

        respuesta = requests.get(API_CARRITO + "/ver",headers=headers)

        if respuesta.status_code == 200:

            datos = respuesta.json()

            return render_template(
                "carrito.html",
                items=datos.get("items", []),
                total=datos.get("total", 0)
            )

        flash("No se pudo cargar el carrito","error")

    except Exception:

        flash("Error al conectar con el servidor","error")

    return render_template("carrito.html",items=[],total=0)


@carrito_bp.route("/agregar/<int:id_producto>")
def agregar_producto(id_producto):

    token = session.get("token")

    if not token:
        flash("Debes iniciar sesión","error")
        return redirect(url_for("usuarios.manejo_login"))

    try:

        headers = {"Authorization":f"Bearer {token}"}

        respuesta = requests.post(API_CARRITO + "/agregar",headers=headers,json={"id_producto": id_producto,"cantidad": 1})

        print("STATUS:", respuesta.status_code)
        print("BODY:", respuesta.text)

        if respuesta.status_code == 200:

            flash("Producto agregado al carrito","success")

        else:

            mensaje = respuesta.json().get("error","No se pudo agregar el producto")

            flash(mensaje,"error")

    except Exception:

        flash("Error al conectar con el servidor","error")

    return redirect(url_for("inicio.pagina_productos"))


@carrito_bp.route("/eliminar/<int:id_producto>")
def eliminar_producto(id_producto):

    token = session.get("token")

    if not token:
        return redirect(url_for("usuarios.manejo_login"))

    try:

        headers = {"Authorization":f"Bearer {token}"}

        requests.delete(API_CARRITO + f"/item/{id_producto}",headers=headers)

    except Exception:

        flash("Error al eliminar producto","error")

    return redirect(url_for("carrito.mostrar_carrito"))


@carrito_bp.route("/actualizar/<int:id_producto>",methods=["POST"])
def actualizar_cantidad(id_producto):

    token = session.get("token")

    if not token:
        return redirect(url_for("usuarios.manejo_login"))

    try:

        cantidad = int(request.form.get("cantidad",1))

        headers = {"Authorization":f"Bearer {token}"}

        requests.put(API_CARRITO + f"/item/{id_producto}",headers=headers,json={"cantidad":cantidad})

    except Exception:

        flash("Error al actualizar cantidad","error")

    return redirect(url_for("carrito.mostrar_carrito"))


@carrito_bp.route("/vaciar")
def vaciar_carrito():

    token = session.get("token")

    if not token:
        return redirect(url_for("usuarios.manejo_login"))

    try:

        headers = {"Authorization":f"Bearer {token}"}

        requests.delete(API_CARRITO + "/vaciar",headers=headers)

        flash("Carrito vaciado","success")

    except Exception:

        flash("Error al vaciar carrito","error")

    return redirect(url_for("carrito.mostrar_carrito"))

@carrito_bp.route("/confirmar")
def confirmar_compra():

    token = session.get("token")

    if not token:
        return redirect(url_for("usuarios.manejo_login"))

    try:

        headers = {"Authorization": f"Bearer {token}"}

        respuesta = requests.post(API_CARRITO + "/confirmar", headers=headers)

        if respuesta.status_code == 200:

            flash("Compra realizada correctamente. Revisa tu correo.", "success")

        else:

            print("STATUS CONFIRMAR:", respuesta.status_code)
            print("BODY CONFIRMAR:", respuesta.text)

            try:
                mensaje = respuesta.json().get("error", "Error al confirmar compra")
            except Exception:
                mensaje = "Error al confirmar compra"

            flash(mensaje, "error")

    except Exception:

        flash("Error al conectar con el servidor", "error")

    return redirect(url_for("carrito.mostrar_carrito"))