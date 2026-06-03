from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from db.db_conn import get_connection

administradores_bp = Blueprint("administradores", __name__)

@administradores_bp.route("/dashboard/stats", methods=["GET"])
@jwt_required()
def dashboard():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        usuario_logueado = get_jwt_identity()
        if usuario_logueado["rol"] != "admin":
            return jsonify({"error": "Acceso denegado"}), 403
        cursor.execute("SELECT COUNT(*) AS total FROM productos")
        total_productos = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM reservas")
        total_reservas = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
        total_usuarios = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) AS total FROM locales")
        total_locales = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reservas
            WHERE estado = 'Confirmada'
        """)
        reservas_confirmadas = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reservas
            WHERE estado = 'Cancelada'
        """)
        reservas_canceladas = cursor.fetchone()["total"]
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM reservas
            WHERE estado = 'En proceso'
        """)
        reservas_en_proceso = cursor.fetchone()["total"]
        return jsonify({
            "mensaje": "Bienvenido al dashboard de administradores",
            "estadisticas": {
                "total_productos": total_productos,
                "total_reservas": total_reservas,
                "total_usuarios": total_usuarios,
                "total_locales": total_locales,
                "reservas_confirmadas": reservas_confirmadas,
                "reservas_canceladas": reservas_canceladas,
                "reservas_en_proceso": reservas_en_proceso,
                "total_ventas": 0,
                "total_clientes": total_usuarios
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@administradores_bp.route("/dashboard/usuarios", methods=["GET"])
@jwt_required()
def obtener_usuarios():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_logueado = get_jwt_identity()
        if usuario_logueado["rol"] != "admin":
            return jsonify({"error": "Acceso denegado"}), 403

        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()



        return jsonify(usuarios), 200
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@administradores_bp.route("/administradores/<int:admin_id>", methods=["GET"])
@jwt_required()
def obtener_administrador(admin_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_logueado = get_jwt_identity()
        if usuario_logueado["rol"] != "admin":
            return jsonify({"error": "Acceso denegado"}), 403
        

        cursor.execute("SELECT * FROM administradores WHERE id = %s", (admin_id,))
        admin = cursor.fetchone()

        if not admin:
            return jsonify({"error": "Administrador no encontrado"}), 404

        return jsonify(admin), 200
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@administradores_bp.route("/usuarios/<int:usuario_id>", methods=["DELETE"])
@jwt_required()
def eliminar_usuario(usuario_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_logueado = get_jwt_identity()
        if usuario_logueado["rol"] != "admin":
            return jsonify({"error": "Acceso denegado"}), 403
        
        validacion_query_busqueda = "SELECT id, rol FROM usuarios WHERE id = %s"
        cursor.execute(validacion_query_busqueda, (usuario_id,))
        usuario_a_eliminar = cursor.fetchone()
        
        if not usuario_a_eliminar:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        if usuario_a_eliminar["rol"] == "admin":
            return jsonify({"error": "No se puede eliminar a un administrador"}), 403
        
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,)) 
        conn.commit()
        return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
    
    except Exception as e:
        return jsonify({"error": "Error en el servidor"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@administradores_bp.route("/administradores/<int:admin_id>", methods=["DELETE"])
@jwt_required()
def eliminar_administrador(admin_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_logueado = get_jwt_identity()
        if usuario_logueado["rol"] != "admin":
            return jsonify({"error": "Acceso denegado"}), 403

        if usuario_logueado["id"] != admin_id:
            return jsonify({"error": "No puedes eliminar a otro administrador"}), 403
        
        validation_query_admin = "SELECT id FROM administradores WHERE id = %s"
        cursor.execute(validation_query_admin, (admin_id,))
        admin_a_eliminar = cursor.fetchone()
        if not admin_a_eliminar:
            return jsonify({"error": "Administrador no encontrado"}), 404
        
        cursor.execute("DELETE FROM administradores WHERE id = %s", (admin_id,))
        conn.commit()
        
        return jsonify({"mensaje": "Administrador eliminado correctamente"}), 200
    
    except Exception as e:
        return jsonify({"error": "Error en el servidor"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@administradores_bp.route("/reseñas/<int:resena_id>", methods=["DELETE"])
@jwt_required()
def eliminar_reseña(reseña_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        usuario_logueado = get_jwt_identity()
        if usuario_logueado["rol"] != "admin":
            return jsonify({"error": "Acceso denegado"}), 403
        
        validacion_query_reseña = "SELECT id FROM reseñas WHERE id = %s"
        cursor.execute(validacion_query_reseña, (reseña_id,))
        reseña_a_eliminar = cursor.fetchone()
        if not reseña_a_eliminar:
            return jsonify({"error": "Reseña no encontrada"}), 404

        cursor.execute("DELETE FROM reseñas WHERE id = %s", (reseña_id,))  
        conn.commit()

        return jsonify({"mensaje": "Reseña eliminada correctamente"}), 200
    
    except Exception as e:
        return jsonify({"error": "Error en el servidor"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()