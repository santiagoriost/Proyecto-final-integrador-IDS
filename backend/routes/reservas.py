from flask import Blueprint, jsonify, request
from db.db_conn import get_connection
from datetime import datetime, timedelta
from flask_mail import Message
from extensions import mail
import uuid
import qrcode
from io import BytesIO

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
                "comentarios": reserva["comentarios"],
                "estado": reserva["estado"],
                "codigo_reserva": reserva["codigo_reserva"],
                "fecha_validacion": str(reserva["fecha_validacion"]) if reserva["fecha_validacion"] else None
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
        comentarios = datos.get("comentarios")
        codigo_reserva = f"RES-{uuid.uuid4().hex[:8].upper()}"
        qr = qrcode.make(codigo_reserva)
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

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
            comentarios,
            estado,
            codigo_reserva
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
            comentarios,
            "En proceso",
            codigo_reserva
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
        🎟️ Código de reserva: {codigo_reserva}

        Presenta este código al llegar al local para validar tu reserva.

        Gracias por reservar en Cafeteria 11.
        """
        mensaje.attach(
            filename=f"qr_reserva_{codigo_reserva}.png",
            content_type="image/png",
            data=qr_buffer.getvalue()
        )
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
                "comentarios": comentarios,
                "estado": "En proceso",
                "codigo_reserva": codigo_reserva
            }
        }), 201
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

        query_historial = """
        INSERT INTO historial_acciones (accion, tipo, detalle)
        VALUES (%s, %s, %s)
        """
        cursor.execute(
            query_historial,
            (
                "Reserva eliminada",
                "reserva",
                f"Se eliminó la reserva #{id_reserva} de {reserva['nombre_cliente']}"
            )
        )

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

@reservas_bp.route("/validar", methods=["PATCH"])
def validar_reserva_por_codigo():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        datos = request.get_json()
        if "codigo_reserva" not in datos:
            return jsonify({"error": "Falta el código de reserva"}), 400
        codigo_reserva = datos["codigo_reserva"].strip()
        if codigo_reserva == "":
            return jsonify({"error": "El código de reserva está vacío"}), 400
        query_buscar = """
        SELECT *
        FROM reservas
        WHERE codigo_reserva = %s
        """
        cursor.execute(query_buscar, (codigo_reserva,))
        reserva = cursor.fetchone()
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404
        if reserva["estado"] == "Cancelada":
            return jsonify({"error": "La reserva está cancelada"}), 400
        if reserva["estado"] in ["Validada", "Asistió"]:
            return jsonify({"error": "La reserva ya fue validada"}), 400
        query_validar = """
        UPDATE reservas
        SET estado = %s,
            fecha_validacion = NOW()
        WHERE id_reserva = %s
        """
        cursor.execute(query_validar, ("Validada", reserva["id_reserva"]))
        query_historial = """
        INSERT INTO historial_acciones (accion, tipo, detalle)
        VALUES (%s, %s, %s)
        """
        cursor.execute(
            query_historial,
            (
                "Reserva validada",
                "reserva",
                f"Se validó la reserva #{reserva['id_reserva']} de {reserva['nombre_cliente']} con código {codigo_reserva}"
            )
        )
        conn.commit()
        return jsonify({
            "mensaje": "Reserva validada correctamente",
            "reserva": {
                "id": reserva["id_reserva"],
                "nombre_cliente": reserva["nombre_cliente"],
                "correo_cliente": reserva["correo_cliente"],
                "fecha_reserva": str(reserva["fecha_reserva"]),
                "hora_reserva": str(reserva["hora_reserva"]),
                "numero_personas": reserva["numero_personas"],
                "estado": "Validada",
                "codigo_reserva": codigo_reserva
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()