from flask import Blueprint, jsonify, request
from db.db_conn import get_connection

reservas_bp = Blueprint("reservas", __name__)

@reservas_bp.route("/", methods=["GET"])
def listar_reservas():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        limit = int(request.args.get("limit", 10))
        offset = int(request.args.get("offset", 0))

        query = "SELECT * FROM reservas LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        listar_reservas = cursor.fetchall()

        if not listar_reservas:
            return jsonify({"error": "reservas no encontradas"}), 404  
        
        query_total = "SELECT COUNT(*) as total FROM reservas"
        cursor.execute(query_total)
        total_reservas = cursor.fetchone()["total"]
        
        reservas = []
        for reserva in listar_reservas:
            reservas.append({
                "id": reserva["id_reserva"],
                "usuario": reserva["usuario_reserva"],
                "producto": reserva["producto_reserva"],
                "fecha_reserva": reserva["fecha_reserva"],
                "fecha_entrega": reserva["fecha_entrega"],
                "estado": reserva["estado"]
            })
        
        base_url = request.base_url

        def build_url(new_offset):
            params = f"limit={limit}&offset={new_offset}"
            return f"{base_url}?{params}"
        
        links = {
            "first": {"href": build_url(0)},
            "last": {"href": build_url(max(total_reservas - (total_reservas % 10), total_reservas - limit))}
        }

        if offset > 0:
            links["prev"] = {"href": build_url(max(offset - limit, 0))}

        if offset + limit < total_reservas:
            links["next"] = {"href": build_url(offset + limit)}

        return jsonify({
            "reservas": reservas,
            "_links": links
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@reservas_bp.route("/", methods=["POST"])
def agregar_reserva():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        datos = request.get_json()

        Atributos_necesarios = ["usuario_reserva", "producto_reserva", "fecha_entrega"]

        for atributo in Atributos_necesarios:
            if atributo not in datos:
                return jsonify({"error": f"Falta el atributo '{atributo}'"}), 400
            if str(datos[atributo]).strip() == "":
                return jsonify({"error": f"El atributo '{atributo}' tiene un valor vacío"}), 400
        query_usuario = "SELECT id_cuenta FROM cuentas WHERE id_cuenta = %s"
        cursor.execute(query_usuario, (datos["usuario_reserva"],))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"error": "usuario no encontrado"}), 404     
        

        query_producto = "SELECT id_producto FROM productos WHERE id_producto = %s"
        cursor.execute(query_producto, (datos["producto_reserva"],))
        producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": "producto no encontrado"}), 404
            
        valores = (
            datos["usuario_reserva"],
            datos["producto_reserva"],
            datos["fecha_entrega"]
        )
            
        query = """
        INSERT INTO reservas (usuario_reserva, producto_reserva, fecha_entrega)
        VALUES (%s, %s, %s)"""
        cursor.execute(query, valores)
        conn.commit()

        return jsonify({
            "id": cursor.lastrowid,
            "usuario_reserva": datos["usuario_reserva"],
            "producto_reserva": datos["producto_reserva"],
            "fecha_entrega": datos["fecha_entrega"],
            "estado": "en proceso"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
 
@reservas_bp.route("/<int:id_reserva>", methods=["GET"])
def obtener_reserva(id_reserva):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM reservas WHERE id_reserva = %s"
        cursor.execute(query, (id_reserva,))
        reserva = cursor.fetchone()

        if not reserva:
            return jsonify({"error": "reserva no encontrada"}), 404

        return jsonify({
            "id": reserva["id_reserva"],
            "usuario": reserva["usuario_reserva"],
            "producto": reserva["producto_reserva"],
            "fecha_reserva": reserva["fecha_reserva"],
            "fecha_entrega": reserva["fecha_entrega"],
            "estado": reserva["estado"]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@reservas_bp.route("/<int:id_reserva>", methods=["DELETE"])
def eliminar_reserva(id_reserva):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM reservas WHERE id_reserva = %s"
        cursor.execute(query, (id_reserva,))
        reserva = cursor.fetchone()

        if not reserva:
            return jsonify({"error": "reserva no encontrada"}), 404

        query_eliminar = "DELETE FROM reservas WHERE id_reserva = %s"
        cursor.execute(query_eliminar, (id_reserva,))
        conn.commit()

        return jsonify({"message": "reserva eliminada correctamente",
                        "reserva_eliminada": reserva
                        }), 200 
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@reservas_bp.route("/<int:id_reserva>", methods=["PUT"])
def actualizar_reserva(id_reserva):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        datos = request.get_json()
        atributos_necesarios = ["usuario_reserva", "producto_reserva", "fecha_entrega", "estado"]

        for atributo in atributos_necesarios:
            if atributo not in datos:
                return jsonify({"error": f"Falta el atributo '{atributo}'"}), 400
            if str(datos[atributo]).strip() == "":
                return jsonify({"error": f"El atributo '{atributo}' tiene un valor vacío"}), 400
        
        query_reserva = "SELECT * FROM reservas WHERE id_reserva = %s"
        cursor.execute(query_reserva, (id_reserva,))
        reserva = cursor.fetchone()

        if not reserva:
            return jsonify({"error": "reserva no encontrada"}), 404

        query_producto = "SELECT id_producto FROM productos WHERE id_producto = %s"
        cursor.execute(query_producto, (datos["producto_reserva"],))
        producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": "producto no encontrado"}), 404

        query_update = """
        UPDATE reservas
        SET usuario_reserva = %s, 
        producto_reserva = %s, 
        fecha_entrega = %s,
        estado = %s
        WHERE id_reserva = %s
        """
        valores = (
            datos["usuario_reserva"],
            datos["producto_reserva"],
            datos["fecha_entrega"],
            datos["estado"],
            id_reserva
        )
        cursor.execute(query_update, valores)
        conn.commit()

        return jsonify({
            "mensaje": "reserva actualizada correctamente",
            "reserva_actualizada": {
                "id": id_reserva,
                "usuario_reserva": datos["usuario_reserva"],
                "producto_reserva": datos["producto_reserva"],
                "fecha_entrega": datos["fecha_entrega"],
                "estado": datos["estado"]
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@reservas_bp.route("/<int:id_reserva>", methods=["PATCH"])
def actualizar_reserva_parcial(id_reserva):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        datos = request.get_json()
        atributos_necesarios = ["usuario_reserva", "producto_reserva", "fecha_entrega", "estado"]

        for atributo in atributos_necesarios:
            if atributo not in datos:
                return jsonify({"error": f"Falta el atributo '{atributo}'"}), 400

            if str(datos[atributo]).strip() == "":
                return jsonify({"error": f"El atributo '{atributo}' tiene un valor vacío"}), 400

        query_reserva = "SELECT * FROM reservas WHERE id_reserva = %s"
        cursor.execute(query_reserva, (id_reserva,))
        reserva = cursor.fetchone()

        if not reserva:
            return jsonify({"error": "reserva no encontrada"}), 404

        query_usuario = "SELECT id_cuenta FROM cuentas WHERE id_cuenta = %s"
        cursor.execute(query_usuario, (datos["usuario_reserva"],))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"error": "usuario no encontrado"}), 404

        query_producto = "SELECT id_producto FROM productos WHERE id_producto = %s"
        cursor.execute(query_producto, (datos["producto_reserva"],))
        producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": "producto no encontrado"}), 404

        query_update = """
        UPDATE reservas
        SET usuario_reserva = %s,
            producto_reserva = %s,
            fecha_entrega = %s,
            estado = %s
        WHERE id_reserva = %s
        """

        valores = (
            datos["usuario_reserva"],
            datos["producto_reserva"],
            datos["fecha_entrega"],
            datos["estado"],
            id_reserva
        )

        cursor.execute(query_update, valores)
        conn.commit()

        return jsonify({
            "mensaje": "reserva actualizada correctamente",
            "reserva_actualizada": {
                "id": id_reserva,
                "usuario_reserva": datos["usuario_reserva"],
                "producto_reserva": datos["producto_reserva"],
                "fecha_entrega": datos["fecha_entrega"],
                "estado": datos["estado"]
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

