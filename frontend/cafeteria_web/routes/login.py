from flask import Blueprint, render_template, request, redirect, flash, url_for
import requests
API_URL = "http://localhost:5001/usuarios/login"
login_bp = Blueprint("login", __name__)

@login_bp.route("/", methods=["GET", "POST"])
def manejo_login():
    if request.method == "POST":
        email = request.form.get("form_email", "").strip()
        clave = request.form.get("form_clave", "").strip()
        if not email or not clave:
            flash('Datos no ingresados.', 'error')
            return redirect(url_for('login.manejo_login'))
        datos_usuario = {
            "email": email,
            "clave": clave
        }
        try:
            respuesta = requests.post(API_URL, json=datos_usuario)
            if respuesta.status_code == 200:
                #datos_api = respuesta.json()
                flash('Inicio de sesion exitoso.', 'success')
                return redirect(url_for('inicio.pagina_inicio'))
        except Exception as e:
            flash('Error con el servidor', 'error')
            return redirect(url_for('inicio.pagina_inicio'))
    return render_template("login.html")
