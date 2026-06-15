from flask import Blueprint, request, jsonify
from db.db_conn import get_connection
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from flask_mail import Message
from extensions import mail

carrito_bp = Blueprint("carrito", __name__)

@carrito_bp.route("/agregar", methods=["POST"])
@jwt_required()
def agregar_producto():

    
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_usuario = int(get_jwt_identity())

        datos = request.get_json()
        id_producto = datos.get("id_producto")
        cantidad = datos.get("cantidad", 1)

        if not id_producto:
            return jsonify({"error": "Debes indicar un producto"}), 400
        
        query_producto = """SELECT * FROM productos WHERE id_producto = %s"""
        cursor.execute(query_producto, (id_producto,))
        producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404
        
        query_carrito = """SELECT id_carrito FROM carritos WHERE usuario_id = %s"""
        cursor.execute(query_carrito, (id_usuario,))
        carrito = cursor.fetchone()
        if not carrito:
            query_crear_carrito = """INSERT INTO carritos(usuario_id) VALUES (%s)"""
            cursor.execute(query_crear_carrito, (id_usuario,))
            conn.commit()
            id_carrito = cursor.lastrowid
        else:
            id_carrito = carrito["id_carrito"]

        query_item = """SELECT * FROM carrito_items WHERE id_carrito = %s AND id_producto = %s"""
        cursor.execute(query_item, (id_carrito, id_producto))
        item = cursor.fetchone()

        if item:
            query_actualizar = """UPDATE carrito_items SET cantidad = cantidad + %s WHERE id_item = %s"""
            cursor.execute(query_actualizar, (cantidad, item["id_item"]))
        else:
            query_agregar = """INSERT INTO carrito_items(id_carrito, id_producto, cantidad) VALUES (%s, %s, %s)"""
            cursor.execute(query_agregar, (id_carrito, id_producto, cantidad))

        conn.commit()

        return jsonify({"message": "Producto agregado al carrito"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error al agregar producto al carrito"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@carrito_bp.route("/ver", methods=["GET"])
@jwt_required()
def ver_carrito():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_usuario = int(get_jwt_identity())

        query = """SELECT p.id_producto, p.nombre, p.precio, p.imagen, ci.cantidad, (p.precio * ci.cantidad) AS subtotal FROM carritos c
                   JOIN carrito_items ci ON c.id_carrito = ci.id_carrito
                   JOIN productos p ON p.id_producto = ci.id_producto
                    WHERE c.usuario_id = %s"""
        cursor.execute(query, (id_usuario,))
        items = cursor.fetchall()
        total = sum(float(i["subtotal"]) for i in items)

        return jsonify({"items": items, "total": total}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error al obtener el carrito"}), 500
    finally:        
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@carrito_bp.route("/item/<int:id_producto>", methods=["PUT"])
@jwt_required()
def actualizar_cantidad(id_producto):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_usuario = int(get_jwt_identity())
        datos = request.get_json()
        cantidad = datos.get("cantidad")

        if cantidad is None or cantidad < 1:
            return jsonify({"error": "Cantidad inválida"}), 400

        query = """UPDATE carrito_items ci
                   JOIN carritos c ON c.id_carrito = ci.id_carrito
                    SET ci.cantidad = %s
                    WHERE c.usuario_id = %s AND ci.id_producto = %s"""
        cursor.execute(query, (cantidad, id_usuario, id_producto))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Producto no encontrado en el carrito"}), 404
        return jsonify({"message": "Cantidad actualizada"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error al actualizar la cantidad"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@carrito_bp.route("/item/<int:id_producto>", methods=["DELETE"])
@jwt_required()
def eliminar_producto(id_producto):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_usuario = int(get_jwt_identity())

        query = """DELETE ci FROM carrito_items ci
                   JOIN carritos c ON c.id_carrito = ci.id_carrito
                    WHERE c.usuario_id = %s AND ci.id_producto = %s"""
        cursor.execute(query, (id_usuario, id_producto))
        conn.commit()

        return jsonify({"message": "Producto eliminado del carrito"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error al eliminar el producto del carrito"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@carrito_bp.route("/confirmar", methods=["POST"])
@jwt_required()
def confirmar_carrito():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        id_usuario = int(get_jwt_identity())
        datos_usuario = get_jwt()

        fecha_mysql = datetime.now().strftime("%Y-%m-%d")
        hora_reserva = datetime.now().strftime("%H:%M:%S")
        comentarios = "pedido realizado desde el carrito"

        query_items = """SELECT p.id_producto, p.nombre, p.stock, ci.cantidad FROM carritos c 
        JOIN carrito_items ci
            ON c.id_carrito = ci.id_carrito
        JOIN productos p
            ON p.id_producto = ci.id_producto
        WHERE c.usuario_id = %s
        """

        cursor.execute(query_items, (id_usuario,))
        items = cursor.fetchall()

        if not items:
            return jsonify({"error": "El carrito está vacío"}), 400

        for item in items:

            if item["stock"] < item["cantidad"]:
                return jsonify({"error": f"Stock insuficiente para {item['id_producto']}"}), 400

        for item in items:

            cursor.execute("""INSERT INTO reservas(nombre_cliente, correo_cliente, tipo_reserva, fecha_reserva, hora_reserva, numero_personas, producto_reserva, comentarios, estado)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (datos_usuario["nombre"], datos_usuario["email"], "Producto", fecha_mysql, hora_reserva, None, item["id_producto"], comentarios, "En proceso")
            )

            cursor.execute(
                """
                UPDATE productos
                SET stock = stock - %s
                WHERE nombre = %s
                """,
                (item["cantidad"], item["nombre"]))

        cursor.execute("""DELETE ci FROM carrito_items ci
                            JOIN carritos c
                                ON c.id_carrito = ci.id_carrito
                            WHERE c.usuario_id = %s""",
                            (id_usuario,))

        conn.commit()

        mail_body = "Tu pedido fue registrado correctamente.\n\n"

        for item in items:
            mail_body += f"- {item['nombre']} x{item['cantidad']}\n"

        mensaje = Message(subject="Pedido confirmado - Cafeteria 11", sender="jcunduri@fi.uba.ar", recipients=[datos_usuario["email"]])

        mensaje.body = mail_body

        mail.send(mensaje)

        return jsonify({"message": "Pedido confirmado"}), 200

    except Exception as e:
        print("ERROR: ", e)
        return jsonify({"error": str(e)}), 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
                

@carrito_bp.route("/vaciar", methods=["DELETE"])
@jwt_required()
def vaciar_carrito():

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        id_usuario = int(get_jwt_identity())

        query = """DELETE ci FROM carrito_items ci
                JOIN carritos c
                    ON ci.id_carrito = c.id_carrito
                WHERE c.usuario_id = %s
                """

        cursor.execute(query, (id_usuario,))
        conn.commit()

        return jsonify({"message": "Carrito vaciado correctamente"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error al vaciar carrito"}), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()
            
        
