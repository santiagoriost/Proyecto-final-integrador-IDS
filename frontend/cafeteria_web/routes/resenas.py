from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
import os


resenas_bp = Blueprint("resenas", __name__)

BACK_APP_HOST = os.environ.get("BACK_APP_HOST", "backend_app")
API_URL = f"http://{BACK_APP_HOST}:5001/resenas"


@resenas_bp.route("/", methods=["GET"])
def pagina_resenas():
    lista_resenas = []
    links = {}
    try:
        limit = request.args.get("_limit", 10)
        offset = request.args.get("_offset", 0)
        respuesta = requests.get(f"{API_URL}?_limit={limit}&_offset={offset}")
        if respuesta.status_code == 200:
            datos = respuesta.json()
            lista_resenas = datos.get("reseñas", [])
            links = datos.get("_links", {})
        else:
            flash("No se pudieron cargar las reseñas","error")
    except Exception:
        flash("Error al conectar con el servidor","error")
    return render_template("resenas.html",resenas=lista_resenas,links=links)

@resenas_bp.route("/agregar", methods=["POST"])
def agregar_resena():
    if not session.get("usuario"):
        flash("Debes iniciar sesión para dejar una reseña","error")
        return redirect(url_for("usuarios.manejo_login"))
    try:
        datos = {
            "id_usuario": session["usuario"]["id"],
            "id_producto": 1,
            "puntuacion": request.form.get("puntuacion"),
            "comentario": request.form.get("comentario")
        }
        respuesta = requests.post(API_URL,json=datos)
        if respuesta.status_code == 201:
            flash("Reseña agregada correctamente","success")
        else:
            flash(respuesta.json().get("error","No se pudo agregar la reseña"),"error")
    except Exception as e:
        flash("Error al conectar con el servidor","error")
    return redirect(url_for("resenas.pagina_resenas"))
