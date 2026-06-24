from flask import Blueprint, jsonify, request
from db.db_conn import get_connection

resenas_bp = Blueprint("resenas", __name__)

def validar_atributos_reseña(datos):
    if not datos:
        return jsonify({"error": "no se especificaron los atributos"}), 400

    atributos_necesarios = ("id_usuario", "id_producto", "puntuacion", "comentario")

    for atributo in atributos_necesarios:
        if atributo not in datos:
            return jsonify({"error": "atributo %s no especificado" % atributo}), 400
        
        if str(datos[atributo]).strip() == "":
            return jsonify({"error": "el atributo %s tiene un valor vacio" % atributo}), 400

        elif atributo in ("id_usuario", "id_producto", "puntuacion") and not str(datos[atributo]).isdigit():
            return jsonify({"error": "atributo %s tiene que ser de tipo INT" % atributo}), 400
        
        elif atributo == "comentario" and not isinstance(datos[atributo], str):
            return jsonify({"error": "el atributo %s tiene que ser tipo str" % atributo}), 400

    if int(datos["puntuacion"]) < 1 or int(datos["puntuacion"]) > 5:
        return jsonify({"error": "la puntuacion tiene que estar entre 1 y 5"}), 400
    

@resenas_bp.route("/", methods=["GET"])
def listar_reseñas():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        limit = int(request.args.get("_limit", 10))
        offset = int(request.args.get("_offset", 0))

        query = """SELECT r.*, u.nombre, u.apellido  FROM resenas r JOIN usuarios u ON r.id_usuario = u.id_usuario LIMIT %s OFFSET %s """
        cursor.execute(query, (limit, offset))
        lista_reseñas = cursor.fetchall()

        if not lista_reseñas:
            return jsonify({"reseñas": [],"_links": {}}), 200

        query_cant_reseñas = "SELECT COUNT(*) as total FROM resenas"
        cursor.execute(query_cant_reseñas)
        cant_reseñas = cursor.fetchone()["total"]

        reseñas = []
        for reseña in lista_reseñas:
            reseñas.append({
                "id": reseña["id_resena"],
                "usuario": reseña["id_usuario"],
                "nombre_usuario": f"{reseña['nombre']} {reseña['apellido']}",
                "producto": reseña["id_producto"],
                "puntuacion": reseña["puntuacion"],
                "respuesta": reseña["respuesta"],
                "comentario": reseña["comentario"]
            })

        base_url = request.base_url

        def build_url(new_offset):
            params = f"_limit={limit}&_offset={new_offset}"
            return f"{base_url}?{params}"

        links = {
            "_first": {"href": build_url(0)},
            "_last": {"href": build_url(max(cant_reseñas - (cant_reseñas % 10), cant_reseñas - limit))}
        }

        if offset > 0:
            links["_prev"] = {"href": build_url(max(offset - limit, 0))}

        if offset + limit < cant_reseñas:
            links["_next"] = {"href": build_url(offset + limit)}

        return jsonify({
            "reseñas": reseñas,
            "_links": links
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@resenas_bp.route("/", methods=["POST"])
def agregar_reseña():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        datos = request.get_json()

        error_validacion = validar_atributos_reseña(datos)
        if error_validacion:
            return error_validacion

        query_usuario = "SELECT id_usuario FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query_usuario, (datos["id_usuario"],))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"error": "usuario no encontrado"}), 404

        query_producto = "SELECT id_producto FROM productos WHERE id_producto = %s"
        cursor.execute(query_producto, (datos["id_producto"],))
        producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": "producto no encontrado"}), 404

        valores = (datos["id_usuario"], datos["id_producto"], datos["puntuacion"], datos["comentario"])
        query = """
        INSERT INTO resenas(id_usuario, id_producto, puntuacion, comentario)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, valores)
        conn.commit()

        return jsonify({
            "id": cursor.lastrowid,
            "usuario": datos["id_usuario"],
            "producto": datos["id_producto"],
            "puntuacion": datos["puntuacion"],
            "comentario": datos["comentario"]
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@resenas_bp.route("/<int:id_resena>", methods=["DELETE"])
def eliminar_reseña(id_resena):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query_validacion = "SELECT id_resena FROM resenas WHERE id_resena = %s"
        cursor.execute(query_validacion, (id_resena,))
        resena = cursor.fetchone()

        if not resena:
            return jsonify({"error": "reseña no encontrada"}), 404

        cursor.execute("DELETE FROM resenas WHERE id_resena = %s", (id_resena,))
        conn.commit()

        return jsonify({"message": "reseña eliminada correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@resenas_bp.route("/<int:id_resena>/respuesta", methods=["PATCH"])
def responder_reseña(id_resena):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        datos = request.get_json()
        respuesta = datos.get("respuesta", "").strip()
        
        if not respuesta:
            return jsonify({"error": "la respuesta no puede estar vacía"}), 400
        
        query = "UPDATE resenas SET respuesta = %s WHERE id_resena = %s"
        cursor.execute(query, (respuesta, id_resena))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "reseña no encontrada"}), 404
        
        return jsonify({"message": "respuesta guardada correctamente"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()