from flask import Blueprint, request, jsonify, render_template, redirect, flash, url_for
import requests
inicio_bp = Blueprint("inicio", __name__)
@inicio_bp.route("/", methods=["GET"])
def pagina_inicio():
    return render_template("inicio.html")
@inicio_bp.route("/reservas", methods=["GET"])
def pagina_reservas():
    return render_template("reservas.html")
@inicio_bp.route("/reservas", methods=["POST"])
def crear_reserva():
    datos_reserva = {
        "nombre_cliente": request.form.get("nombre_cliente"),
        "correo_cliente": request.form.get("correo_cliente"),
        "fecha_reserva": request.form.get("fecha_reserva"),
        "hora_reserva": request.form.get("hora_reserva"),
        "numero_personas": request.form.get("numero_personas"),
        "tipo_reserva": request.form.get("tipo_reserva"),
        "comentarios": request.form.get("comentarios")
    }
    try:
        respuesta = requests.post(
            "http://localhost:5001/reservas/",
            json=datos_reserva
        )
        if respuesta.status_code == 201:
            flash(
                "Reserva realizada con éxito. Se ha enviado un correo de confirmación.",
                "success"
            )
        else:
            mensaje_error = respuesta.json().get(
                "error",
                "No se pudo realizar la reserva."
            )
            flash(mensaje_error, "error")
    except Exception:
        flash(
            "Error al conectar con el servidor.",
            "error"
        )
    return redirect(
        url_for("inicio.pagina_reservas")
    )