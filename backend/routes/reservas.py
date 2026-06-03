from flask import Blueprint, jsonify, request
from db.db_conn import get_connection
from datetime import datetime, timedelta
from flask_mail import Message
from extensions import mail

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
                "nombre_cliente": reserva["nombre_cliente"],
                "correo_cliente": reserva["correo_cliente"],
                "tipo_reserva": reserva["tipo_reserva"],
                "fecha_reserva": str(reserva["fecha_reserva"]),
                "hora_reserva": str(reserva["hora_reserva"]),
                "numero_personas": reserva["numero_personas"],
                "producto_reserva": reserva["producto_reserva"],
                "comentarios": reserva["comentarios"],
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

        atributos_necesarios = [
            "nombre_cliente",
            "correo_cliente",
            "tipo_reserva",
            "fecha_reserva",
            "hora_reserva"
        ]

        for atributo in atributos_necesarios:
            if atributo not in datos:
                return jsonify({"error": f"Falta el atributo '{atributo}'"}), 400

            if str(datos[atributo]).strip() == "":
                return jsonify({"error": f"El atributo '{atributo}' tiene un valor vacío"}), 400

        nombre_cliente = datos["nombre_cliente"]
        correo_cliente = datos["correo_cliente"]
        tipo_reserva = datos["tipo_reserva"]
        fecha_reserva = datos["fecha_reserva"]
        fecha_mysql = datetime.strptime(
            fecha_reserva,
            "%d/%m/%Y"
        ).strftime("%Y-%m-%d")
        hora_reserva = datos["hora_reserva"]
        numero_personas = datos.get("numero_personas")
        producto_reserva = datos.get("producto_reserva")
        comentarios = datos.get("comentarios")

        fecha_hora_reserva = datetime.strptime(
            f"{fecha_reserva} {hora_reserva}",
            "%d/%m/%Y %H:%M"
        )

        limite_inicio = fecha_hora_reserva - timedelta(minutes=20)
        limite_fin = fecha_hora_reserva + timedelta(minutes=20)
        query_validar_reserva = """
        SELECT id_reserva
        FROM reservas
        WHERE fecha_reserva = %s
        AND TIMESTAMP(fecha_reserva, hora_reserva) BETWEEN %s AND %s
        AND estado != 'Cancelada'
        """
        cursor.execute(
            query_validar_reserva,
            (fecha_mysql, limite_inicio, limite_fin)
        )
        reserva_existente = cursor.fetchone()
        if reserva_existente:
            return jsonify({
                "error": "Ya existe una reserva asociada a este correo en un rango cercano de 20 minutos"
            }), 400
        query_insertar = """
        INSERT INTO reservas (
            nombre_cliente,
            correo_cliente,
            tipo_reserva,
            fecha_reserva,
            hora_reserva,
            numero_personas,
            producto_reserva,
            comentarios,
            estado
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            nombre_cliente,
            correo_cliente,
            tipo_reserva,
            fecha_mysql,
            hora_reserva,
            numero_personas,
            producto_reserva,
            comentarios,
            "En proceso"
        )
        cursor.execute(query_insertar, valores)
        conn.commit()
        mensaje = Message(
            subject="Reserva confirmada - Cafeteria 11",
            sender="jcunduri@fi.uba.ar",
            recipients=[correo_cliente]
        )

        mensaje.body = f"""
        Hola {nombre_cliente},

        Tu reserva fue realizada con éxito 😎

        📅 Fecha: {fecha_reserva}
        ⏰ Hora: {hora_reserva}
        👥 Personas: {numero_personas}
        ☕ Tipo: {tipo_reserva}

        Gracias por reservar en Cafeteria 11.
        """
        mail.send(mensaje)

        return jsonify({
            "id": cursor.lastrowid,
            "mensaje": "Reserva creada correctamente",
            "reserva": {
                "nombre_cliente": nombre_cliente,
                "correo_cliente": correo_cliente,
                "tipo_reserva": tipo_reserva,
                "fecha_reserva": fecha_reserva,
                "hora_reserva": hora_reserva,
                "numero_personas": numero_personas,
                "producto_reserva": producto_reserva,
                "comentarios": comentarios,
                "estado": "En proceso"
            }
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
            "fecha_entrega": reserva["hora_reserva"],
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

        return jsonify({
            "message": "reserva eliminada correctamente"
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@reservas_bp.route("/<int:id_reserva>/estado", methods=["PATCH"])
def actualizar_estado_reserva(id_reserva):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        datos = request.get_json()

        if "estado" not in datos:
            return jsonify({"error": "Falta el estado"}), 400

        nuevo_estado = datos["estado"]

        query = "SELECT * FROM reservas WHERE id_reserva = %s"
        cursor.execute(query, (id_reserva,))
        reserva = cursor.fetchone()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        query_update = """
        UPDATE reservas
        SET estado = %s
        WHERE id_reserva = %s
        """

        cursor.execute(query_update, (nuevo_estado, id_reserva))
        conn.commit()

        mensaje = Message(
            subject="Actualización de reserva - Cafeteria 11",
            sender="jcunduri@fi.uba.ar",
            recipients=[reserva["correo_cliente"]]
        )

        mensaje.body = f"""
            Hola {reserva["nombre_cliente"]},

            El estado de tu reserva fue actualizado 😎

            Nuevo estado: {nuevo_estado}

            📅 Fecha: {reserva["fecha_reserva"]}
            ⏰ Hora: {reserva["hora_reserva"]}

            Gracias por usar Cafeteria 11.
            """
        mail.send(mensaje)
        return jsonify({
            "mensaje": "Estado actualizado correctamente",
            "nuevo_estado": nuevo_estado
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

