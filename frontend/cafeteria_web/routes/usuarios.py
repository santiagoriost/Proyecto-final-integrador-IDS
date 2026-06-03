from flask import Blueprint, render_template, request, redirect, flash, url_for, session
import requests
API_URL = "http://localhost:5001/usuarios/login"
API_REGISTER = "http://localhost:5001/usuarios/register"
usuarios_bp = Blueprint("usuarios", __name__)

@usuarios_bp.route("/login/", methods=["GET", "POST"])
def manejo_login():
    if request.method == "POST":
        email = request.form.get("form_email", "").strip()
        clave = request.form.get("form_clave", "").strip()
        if not email or not clave:
            flash('Datos no ingresados.', 'error')
            return redirect(url_for('usuarios.manejo_login'))
        datos_usuario = {
            "email": email,
            "clave": clave
        }
        try:
            respuesta = requests.post(API_URL, json=datos_usuario)
            if respuesta.status_code == 200:
                datos_api = respuesta.json()
                session["token"] = datos_api.get("token")
                flash('Inicio de sesion exitoso.', 'success')
                return redirect(url_for('inicio.pagina_inicio'))
            elif respuesta.status_code == 404:
                flash('Datos incorrectos, usuario no encontrado', 'error')
        except Exception as e:
            flash('Error con el servidor', 'error')
    return render_template("login.html")

@usuarios_bp.route("/register/", methods=["GET", "POST"])
def manejo_register():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        email = request.form.get("email", "").strip()
        clave = request.form.get("clave", "").strip()
        if not nombre or not apellido or not email or not clave:
            flash('Datos no ingresados.', 'error')
            return redirect(url_for('usuarios.manejo_register'))
        
        datos_usuario = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "clave": clave
        }
        try:
            respuesta = requests.post(API_REGISTER, json=datos_usuario)
            if respuesta.status_code == 201:
                flash('Registro exitoso. Por favor, inicie sesión.', 'success')
                return redirect(url_for('usuarios.manejo_login'))
            elif respuesta.status_code == 400:
                flash('Error en el registro. Verifique los datos ingresados.', 'error')
        
        except Exception as e:
            print ("error:", e)
            flash(f"Error con el servidor: {str(e)}", 'error')
    
    return render_template("register.html")