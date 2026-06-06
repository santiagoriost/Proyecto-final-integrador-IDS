from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

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

        if not nombre or not email or not clave:
            return jsonify({
                "error": "Todos los campos son obligatorios"
            }), 400

        if not rol:
            rol = "user"

        query_validacion_email = """
        SELECT id_usuario
        FROM usuarios
        WHERE correo = %s
        """

        cursor.execute(query_validacion_email, (email,))

        if cursor.fetchone():
            return jsonify({
                "error": "El email ya está registrado"
            }), 400

        clave_hashed = bcrypt.generate_password_hash(
            clave
        ).decode("utf-8")

        query_insert = """
        INSERT INTO usuarios(
            nombre,
            apellido,
            correo,
            contraseña,
            rol
        )
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            query_insert,
            (
                nombre,
                apellido,
                email,
                clave_hashed,
                rol
            )
        )

        conn.commit()

        return jsonify({
            "id": cursor.lastrowid,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "rol": rol
        }), 201

    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500

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
            return jsonify({
                "error": "Faltan campos obligatorios"
            }), 400

        query_usuario = """
        SELECT *
        FROM usuarios
        WHERE correo = %s
        """

        cursor.execute(query_usuario, (email,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({
                "error": "Usuario no encontrado"
            }), 404

        password_valida = bcrypt.check_password_hash(
            usuario["contraseña"],
            clave
        )

        if not password_valida:
            return jsonify({
                "error": "Contraseña incorrecta"
            }), 401

        email_usuario = (
            usuario.get("correo")
            or usuario.get("email")
        )

        claims = {
            "nombre": usuario["nombre"],
            "apellido": usuario.get("apellido", ""),
            "email": email_usuario,
            "rol": usuario["rol"]
        }

        token = create_access_token(
            identity=str(usuario["id_usuario"]),
            additional_claims=claims
        )

        return jsonify({
            "message": "Login exitoso",
            "token": token,
            "usuario": {
                "id": usuario["id_usuario"],
                "nombre": usuario["nombre"],
                "apellido": usuario.get("apellido", ""),
                "email": email_usuario,
                "rol": usuario["rol"]
            }
        }), 200

    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


@usuarios_bp.route("/logout", methods=["POST"])
def logout():

    return jsonify({
        "message": "Logout exitoso"
    }), 200


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

        return jsonify({
            "usuario": {
                "id": id_usuario,
                "nombre": datos_usuario.get("nombre"),
                "apellido": datos_usuario.get("apellido"),
                "email": datos_usuario.get("email"),
                "rol": datos_usuario.get("rol")
            }
        }), 200

    except Exception as e:

        datos = request.get_json()
        email = datos.get("email")
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

        msg = Message("Restablecer contraseña", recipients=[email], sender="jcunduri@fi.uba.ar")
        msg.body = f"Hola,\n\nRecibimos una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para restablecerla:\n\n{reset_link}\n\nSi no solicitaste este cambio, puedes ignorar este correo.\n\nSaludos."
        mail.send(msg)


        return jsonify({"message": "Se mando el mail para restablecer tu contraseña", "reset_link": reset_link}), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()