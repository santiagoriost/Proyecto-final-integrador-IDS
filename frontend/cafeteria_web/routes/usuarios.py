from flask import Blueprint, render_template, request, redirect, flash, url_for, session
import requests
import os
BACK_APP_HOST = os.environ.get("BACK_APP_HOST", "backend_app")
API_URL = f"http://{BACK_APP_HOST}:5001/usuarios/login"
API_REGISTER = f"http://{BACK_APP_HOST}:5001/usuarios/register"
API_FORGOT_PASSWORD = f"http://{BACK_APP_HOST}:5001/usuarios/forgot-password"
API_RESET_PASSWORD = f"http://{BACK_APP_HOST}:5001/usuarios/reset-password"
API_PERFIL = f"http://{BACK_APP_HOST}:5001/usuarios/me"
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
                session["usuario"] = datos_api.get("usuario", {})
                session["rol"] = datos_api.get("usuario", {}).get("rol")

                flash('Inicio de sesion exitoso.', 'success')

                if session["rol"] == "admin":
                        return redirect(url_for("dashboard.dashboard_reservas"))

                return redirect(url_for("inicio.pagina_inicio"))
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

@usuarios_bp.route("/forgot-password/", methods=["GET", "POST"])
def manejo_forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            flash('Correo electrónico no ingresado.', 'error')
            return redirect(url_for('usuarios.manejo_forgot_password'))
        
        datos_email = {
            "email": email
        }
        try:
            respuesta = requests.put(API_FORGOT_PASSWORD, json=datos_email)
            if respuesta.status_code == 200:
                flash('Se ha enviado un correo para restablecer tu contraseña.', 'success')
                return redirect(url_for('usuarios.manejo_login'))
            elif respuesta.status_code == 404:
                flash('usuario no encontrado.', 'error')
        except Exception as e:
            flash('Error con el servidor', 'error')
    return render_template("forgot_password.html")

@usuarios_bp.route("/reset-password/", methods=["GET", "POST"])
def manejo_reset_password():
    token = request.args.get("token")
    if request.method == "POST":
        token = request.form.get("token")
        nueva_clave = request.form.get("nueva_clave", "").strip()
        if not nueva_clave:
            flash('Nueva contraseña no ingresada.', 'error')
            return redirect(url_for('usuarios.manejo_reset_password', token=token))
        confirmar_clave = request.form.get("confirmar_clave", "").strip()
        if nueva_clave != confirmar_clave:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('usuarios.manejo_reset_password', token=token))
        datos_reset = {
            "reset_token": token,
            "nueva_clave": nueva_clave
        }
        try:
            respuesta = requests.post(API_RESET_PASSWORD, json=datos_reset)
            if respuesta.status_code == 200:
                flash('Contraseña restablecida correctamente. Por favor, inicie sesión.', 'success')
                return redirect(url_for('usuarios.manejo_login'))
            elif respuesta.status_code == 400:
                flash('Token inválido o expirado.', 'error')
        except Exception as e:
            flash('Error con el servidor', 'error')
    return render_template("reset_password.html", token=token)

@usuarios_bp.route("/logout/")
def manejo_logout():
    session.pop("token", None)
    session.pop("usuario", None)
    session.pop("rol", None)
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('inicio.pagina_inicio'))

@usuarios_bp.route("/perfil/")
def manejo_perfil():
    token = session.get("token")
    if not token:
        flash('Debes iniciar sesión para ver tu perfil.', 'error')
        return redirect(url_for('usuarios.manejo_login'))
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        respuesta = requests.get(API_PERFIL, headers=headers)
        if respuesta.status_code != 200:
            flash('Error al obtener el perfil.', 'error')
            return redirect(url_for('inicio.pagina_inicio'))
        datos_perfil = respuesta.json()
        return render_template("perfil.html", usuario=datos_perfil.get("usuario"))
    except Exception as e:
        flash(f'Error con el servidor: {str(e)}', 'error')
        return redirect(url_for('inicio.pagina_inicio'))
    
    