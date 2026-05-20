from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.db_conn import get_connection

locales_bp = Blueprint("locales", __name__)

@locales_bp.route("/locales", methods=["GET"])
def mostrar_locales():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM locales"
        cursor.execute(query)
        lista_locales = cursor.fetchall()

        if not lista_locales:
            return jsonify({"error": "locales no encontrados"}), 404

        locales = []
        for local in lista_locales:
            locales.append({
                "id": local["id_local"],
                "nombre": local["nombre"],
                "direccion": local["direccion"],
                "telefono": local["telefono"]
            })

        return jsonify(locales), 200

    except Exception as e:
        return jsonify({"error al obtener los locales": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@locales_bp.route("/locales", methods=["POST"])
@jwt_required()
def agregar_locales():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        user = get_jwt_identity()

        if user["rol"] != "admin":
            return jsonify({"error": "no autorizado"}), 403
        
        data = request.get_json()
        nombre = data.get("nombre")
        pais = data.get("pais")
        provincia = data.get("provincia")
        direccion = data.get("direccion")
        horario_apertura = data.get("horario_apertura")
        horario_cierre = data.get("horario_cierre")

        if not all([nombre, pais, provincia, direccion, horario_apertura, horario_cierre]):
            return jsonify({"error": "todos los campos son obligatorios"}), 400
        
        query = "INSERT INTO locales (nombre, pais, provincia, direccion, horario_apertura, horario_cierre) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (nombre, pais, provincia, direccion, horario_apertura, horario_cierre))
        conn.commit()

        return jsonify({"message": "local agregado correctamente"}), 201

    except Exception as e:
        return jsonify({"error al agregar el local": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@locales_bp.route("/locales/<int:id_local>", methods=["DELETE"])
@jwt_required()
def eliminar_local(id_local):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        user = get_jwt_identity()

        if user["rol"] != "admin":
            return jsonify({"error": "no autorizado"}), 403
        
        query = "SELECT * FROM locales WHERE id_local = %s"
        cursor.execute(query, (id_local,))
        local = cursor.fetchone()

        if not local:
            return jsonify({"error": "local no encontrado"}), 404
        
        query = "DELETE FROM locales WHERE id_local = %s"
        cursor.execute(query, (id_local,))
        conn.commit()

        return jsonify({"message": "local eliminado correctamente"}), 200
    
    except Exception as e:
        return jsonify({"error al eliminar el local": str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@locales_bp.route("/locales/<int:id_local>", methods=["PUT"])
@jwt_required()
def actualizar_local(id_local):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        user = get_jwt_identity()

        if user["rol"] != "admin":
            return jsonify({"error": "no autorizado"}), 403
        
        data = request.get_json()
        nombre = data.get("nombre")
        pais = data.get("pais")
        provincia = data.get("provincia")
        direccion = data.get("direccion")
        horario_apertura = data.get("horario_apertura")
        horario_cierre = data.get("horario_cierre")

        query = "SELECT * FROM locales WHERE id_local = %s"
        cursor.execute(query, (id_local,))
        local = cursor.fetchone()

        if not local:
            return jsonify({"error": "local no encontrado"}), 404
        
        query = "UPDATE locales SET nombre = %s, pais = %s, provincia = %s, direccion = %s, horario_apertura = %s, horario_cierre = %s WHERE id_local = %s"
        cursor.execute(query, (nombre, pais, provincia, direccion, horario_apertura, horario_cierre, id_local))
        conn.commit()

        return jsonify({"message": "local actualizado correctamente"}), 200
    
    except Exception as e:
        return jsonify({"error al actualizar el local": str(e)}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()