from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from db.db_conn import get_connection
import secrets 
from datetime import timedelta, datetime
from flask_mail import Message
from extensions import mail
import traceback


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
        rol = datos.get("rol")
        if not nombre or not apellido or not email or not clave:
            return jsonify({"error": "Todos los campos son obligatorios"}), 400
        if not rol:
            rol = "user"
        query_validacion_email = "SELECT id_usuario FROM usuarios WHERE email = %s"
        cursor.execute(query_validacion_email, (email,))
        if cursor.fetchone():
            return jsonify({"error": "El email ya está registrado"}), 400
        
        clave_hashed = bcrypt.generate_password_hash(clave).decode("utf-8")
        
        query_insert = """
        INSERT INTO usuarios(nombre, apellido, email, clave, rol)
        VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query_insert, (nombre, apellido, email, clave_hashed, rol))
        conn.commit()
        
        return jsonify({
            "id": cursor.lastrowid,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "rol": rol
        }), 201
    except Exception as e:
        print("error:", e)
        traceback.print_exc()
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
        
        query_usuario = "SELECT * FROM usuarios WHERE correo = %s"
        cursor.execute(query_usuario, (email,))
        usuario = cursor.fetchone()

        if not usuario: 
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        password_valida = bcrypt.check_password_hash(usuario["contraseña"], clave)
        if not password_valida:
            return jsonify({"error": "Contraseña incorrecta"}), 401
        
        claims = {
            "nombre": usuario["nombre"],
            "apellido": usuario["apellido"],
            "email": usuario["correo"],
            "rol": usuario["rol"]
        }
        token = create_access_token(identity=str(usuario["id_usuario"]), additional_claims=claims)
        
        return jsonify({"message": "Login exitoso", "token": token, "usuario": {
            "id": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "apellido": usuario["apellido"],
            "email": usuario["email"],
            "rol": usuario["rol"]
        }}), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()

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

@usuarios_bp.route("/me", methods=["GET"])
@jwt_required()
def mostrar_perfil():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_usuario = get_jwt_identity()
        datos_usuario = get_jwt()
        return jsonify({"usuario": { "id": id_usuario, "nombre": datos_usuario.get("nombre"), "apellido": datos_usuario.get("apellido"), "email": datos_usuario.get("email"), "rol": datos_usuario.get("rol")}}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route("/", methods=["GET"])
@jwt_required()
def mostrar_usuarios():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        #id_usuario = get_jwt_identity()
        datos_usuario = get_jwt()
        if datos_usuario.get("rol") != "admin":
            return jsonify({"error": "Acceso denegado"}), 403
        
        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))

        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        total_usuarios = cursor.fetchone()["total"]
        
        query_mostrar_users = "SELECT * FROM usuarios LIMIT %s OFFSET %s"
        cursor.execute(query_mostrar_users, (limit, offset))
        usuarios = cursor.fetchall()

        usuarios_a_mostrar = []
        for usuario in usuarios:
            usuarios_a_mostrar.append({
                "id": usuario["id_usuario"],
                "nombre": usuario["nombre"],
                "apellido": usuario["apellido"],
                "email": usuario["email"],
                "rol": usuario["rol"]
            })

        base_url = request.base_url
        def build_url(new_offset):
            return f"{base_url}?limit={limit}&offset={new_offset}"

        links = {
            "first": {"href": build_url(0)},
            "last": {"href": build_url(max(total_usuarios - (total_usuarios % limit), total_usuarios - limit))}
        }

        if offset > 0:
            links["prev"] = {"href": build_url(max(offset - limit, 0))}

        if offset + limit < total_usuarios:
            links["next"] = {"href": build_url(offset + limit)}
            
        
        return jsonify({
            "usuarios": usuarios_a_mostrar,
            "total": total_usuarios,
            "_links": links
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def mostrar_usuario(id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        #id_usuario = get_jwt_identity()
        datos_usuario = get_jwt()
        
        if datos_usuario.get("rol") != "admin":
            return jsonify({"error": "Acceso denegado"}), 403
        
        query_mostrar_user = "SELECT * FROM usuarios WHERE id_usuario = %s"

        cursor.execute(query_mostrar_user, (id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        usuario_a_mostrar = {"id": usuario["id_usuario"], "nombre": usuario["nombre"], "apellido": usuario["apellido"], "email": usuario["email"], "rol": usuario["rol"]}
        return jsonify({"usuario": usuario_a_mostrar}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()
  
@usuarios_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def modificar_usuario(id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_usuario = get_jwt_identity()
        datos_usuario = get_jwt()

        if datos_usuario.get("rol") != "admin" and id_usuario != str(id):
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

@usuarios_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def eliminar_usuario(id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_usuario = get_jwt_identity()
        datos_usuario = get_jwt()
        if datos_usuario.get("rol") != "admin" and id_usuario != str(id):
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

        reset_link = f"http://localhost:5002/reset-password?token={reset_token}"

        msg = Message("Restablecer contraseña", recipients=[email])
        msg.body = f"Hola,\n\nRecibimos una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para restablecerla:\n\n{reset_link}\n\nSi no solicitaste este cambio, puedes ignorar este correo.\n\nSaludos."
        mail.send(msg)

        return jsonify({"message": "Se mando el mail para restablecer tu contraseña", "reset_link": reset_link}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@usuarios_bp.route("/reset-password", methods=["POST"])
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
        
        query_validacion_token = "SELECT id_usuario, reset_token_expiration FROM usuarios WHERE reset_token = %s"
        cursor.execute(query_validacion_token, (reset_token,))
        usuario = cursor.fetchone()
        if not usuario:
            return jsonify({"error": "Token inválido"}), 400
        
        if usuario["reset_token_expiration"] < datetime.now():
            return jsonify({"error": "Token expirado"}), 400
        
        nueva_clave_hashed = bcrypt.generate_password_hash(nueva_clave).decode("utf-8")
        query_actualizar_clave = "UPDATE usuarios SET clave = %s, reset_token = NULL, reset_token_expiration = NULL WHERE id_usuario = %s"
        cursor.execute(query_actualizar_clave, (nueva_clave_hashed, usuario["id_usuario"]))
        conn.commit()

        return jsonify({"message": "Contraseña restablecida correctamente"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

        