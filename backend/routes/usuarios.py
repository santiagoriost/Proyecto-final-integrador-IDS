from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from db.db_conn import get_connection
import secrets 
from datetime import timedelta, datetime


usuarios_bp = Blueprint("usuarios", __name__)
bcrypt = Bcrypt()

@usuarios_bp.route("/register", methods=["POST"])
def register():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        datos = request.get_json()
        nombre = datos.get("nombre")
        apellido = datos.get("apellido")
        email = datos.get("email")
        clave = datos.get("clave")

        if not nombre or not apellido or not email or not clave:
            return jsonify({"error": "Todos los campos son obligatorios"}), 400
        
        query_validacion_email = "SELECT id_usuario FROM usuarios WHERE email = %s"
        cursor.execute(query_validacion_email, (email,))
        if cursor.fetchone():
            return jsonify({"error": "El email ya está registrado"}), 400
        
        clave_hashed = bcrypt.generate_password_hash(clave).decode("utf-8")
        
        query_insert = """
        INSERT INTO usuarios(nombre, apellido, email, clave)
        VALUES (%s, %s, %s, %s)"""
        cursor.execute(query_insert, (nombre, apellido, email, clave_hashed))
        conn.commit()
        
        return jsonify({
            "id": cursor.lastrowid,
            "nombre": nombre,
            "apellido": apellido,
            "email": email
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route("/login", methods=["POST"])
def login():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        datos = request.get_json()
        email = datos.get("email")
        clave = datos.get("clave")
        
        if not email or not clave:
            return jsonify({"error": "Faltan campos obligatorios"}), 400
        
        query_usuario = "SELECT * FROM usuarios WHERE email = %s"
        cursor.execute(query_usuario, (email,))
        usuario = cursor.fetchone()

        if not usuario: 
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        password_valida = bcrypt.check_password_hash(usuario["clave"], clave)
        if not password_valida:
            return jsonify({"error": "Contraseña incorrecta"}), 401
        
        token = create_access_token(identity= { "id": usuario["id_usuario"], "email": usuario["email"], "rol": usuario["rol"] })
        
        return jsonify({"message": "Login exitoso", "token": token, "usuario": {
            "id": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "apellido": usuario["apellido"],
            "email": usuario["email"],
            "rol": usuario["rol"]
        }}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()    

@usuarios_bp.route("/logout", methods=["POST"])
def logout():
    #Aca el logout se maneja en el front end asi que aca no va mas nada
    return jsonify({"message": "Logout exitoso"}), 200

@usuarios_bp.route("/profile", methods=["GET"])
@jwt_required()
def mostrar_perfil():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_actual = get_jwt_identity()

        return jsonify({"usuario": { "id": usuario_actual["id"], "nombre": usuario_actual["email"], "rol": usuario_actual["rol"]}}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route("/usuarios", methods=["GET"])
@jwt_required()
def mostrar_usuarios():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_logueado = get_jwt_identity()
        
        if usuario_logueado["rol"] != "admin":
            return jsonify({"error": "Acceso denegado"}), 403
        
        query_mostrar_users = "SELECT * FROM usuarios"

        cursor.execute(query_mostrar_users)
        usuarios = cursor.fetchall()
        
        return jsonify({"usuarios": usuarios}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route("/usuarios/<int:id>", methods=["GET"])
@jwt_required()
def mostrar_usuario(id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_logueado = get_jwt_identity()
        
        if usuario_logueado["rol"] != "admin" and usuario_logueado["id"] != id:
            return jsonify({"error": "Acceso denegado"}), 403
        
        query_mostrar_user = "SELECT * FROM usuarios WHERE id_usuario = %s"

        cursor.execute(query_mostrar_user, (id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify({"usuario": usuario}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()
  
@usuarios_bp.route("/usuarios/<int:id>", methods=["PUT"])
@jwt_required()
def modificar_usuario(id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_logueado = get_jwt_identity()

        if usuario_logueado["rol"] != "admin" and usuario_logueado["id"] != id:
            return jsonify({"error": "Acceso denegado"}), 403

        datos = request.get_json()
        nombre = datos.get("nombre")
        apellido = datos.get("apellido")
        email = datos.get("email")
        
        if not nombre or not apellido or not email:
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        query_actualizar_user = "UPDATE usuarios SET nombre = %s, apellido = %s, email = %s WHERE id_usuario = %s"

        cursor.execute(query_actualizar_user, (nombre, apellido, email, id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404

        return jsonify({"message": "Usuario actualizado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route("/usuarios/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_usuario(id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_logueado = get_jwt_identity()

        if usuario_logueado["rol"] != "admin" and usuario_logueado["id"] != id:
            return jsonify({"error": "Acceso denegado"}), 403
        
        validation_query = "SELECT id_usuario FROM usuarios WHERE id_usuario = %s"
        cursor.execute(validation_query, (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Usuario no encontrado"}), 404

        query_eliminar_user = "DELETE FROM usuarios WHERE id_usuario = %s"

        cursor.execute(query_eliminar_user, (id,))
        conn.commit()

        return jsonify({"message": "Usuario eliminado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route("/forgot-password", methods=["PUT"])
def forgot_password():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        datos = request.get_json()
        email = datos.get ("email")
        if not email:
            return jsonify({"error": "El campo email es obligatorio"}), 400
        
        query_usuario = "SELECT id_usuario FROM usuarios WHERE email = %s"
        cursor.execute(query_usuario, (email,))
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        reset_token = secrets.token_hex(32)
        expiration_time = datetime.now() + timedelta(hours=1)
        actualizar_token_query = "UPDATE usuarios SET reset_token = %s, reset_token_expiration = %s WHERE id_usuario = %s"
        cursor.execute(actualizar_token_query, (reset_token, expiration_time, usuario["id_usuario"]))
        conn.commit()

        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

        #aca se manda el mail con el link pero se hace con el front tambien

        return jsonify({"message": "Se mando el mail para restablecer tu contraseña", "reset_link": reset_link}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route("/change-password", methods=["POST"])
def change_password():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        data = request.get_json()
        reset_token = data.get("reset_token")
        nueva_clave = data.get("nueva_clave")

        if not reset_token or not nueva_clave:
            return jsonify({"error": "Faltan campos obligatorios"}), 400
        
        query_validar_token = "SELECT id_usuario, reset_token_expiration FROM usuarios WHERE reset_token = %s"
        cursor.execute(query_validar_token, (reset_token,))
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({"error": "Token inválido"}), 400
        
        nueva_clave_hashed = bcrypt.generate_password_hash(nueva_clave).decode("utf-8")

        query_actualizar_clave = "UPDATE usuarios SET clave = %s, reset_token = NULL, reset_token_expiration = NULL WHERE id_usuario = %s"
        cursor.execute(query_actualizar_clave, (nueva_clave_hashed, usuario["id_usuario"]))
        conn.commit()

        return jsonify({"message": "Contraseña actualizada correctamente"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

        