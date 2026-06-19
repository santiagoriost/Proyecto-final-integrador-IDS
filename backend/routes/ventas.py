from flask import Blueprint, jsonify, request
from db.db_conn import get_connection

ventas_bp = Blueprint("ventas", __name__)
@ventas_bp.route("/", methods=["GET"])
def listar_ventas():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT *
            FROM ventas
            ORDER BY fecha_venta DESC
        """)
        ventas = cursor.fetchall()
        return jsonify({"ventas": ventas}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@ventas_bp.route("/<int:id_venta>", methods=["GET"])
def detalle_venta(id_venta):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM ventas
            WHERE id_venta = %s
        """, (id_venta,))
        venta = cursor.fetchone()

        if not venta:
            return jsonify({"error": "Venta no encontrada"}), 404

        cursor.execute("""
            SELECT 
                p.nombre,
                dv.cantidad,
                dv.precio_unitario,
                dv.subtotal
            FROM detalle_ventas dv
            JOIN productos p ON p.id_producto = dv.producto_id
            WHERE dv.venta_id = %s
        """, (id_venta,))
        detalles = cursor.fetchall()

        return jsonify({
            "venta": venta,
            "detalles": detalles
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()           
@ventas_bp.route("/", methods=["POST"])
def registrar_venta():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        datos = request.get_json()
        productos = datos.get("productos", [])

        if not productos:
            return jsonify({"error": "Debe enviar productos"}), 400
        total_venta = 0
        detalle_calculado = []
        for item in productos:
            producto_id = item.get("producto_id")
            cantidad = int(item.get("cantidad", 0))
            if not producto_id or cantidad <= 0:
                return jsonify({"error": "Producto o cantidad inválida"}), 400
            cursor.execute(
                "SELECT * FROM productos WHERE id_producto = %s",
                (producto_id,)
            )
            producto = cursor.fetchone()
            if not producto:
                return jsonify({"error": f"Producto {producto_id} no existe"}), 404

            if producto["stock"] < cantidad:
                return jsonify({
                    "error": f"Stock insuficiente para {producto['nombre']}"
                }), 400
            precio_unitario = producto["precio"]
            subtotal = precio_unitario * cantidad
            total_venta += subtotal
            detalle_calculado.append({
                "producto_id": producto_id,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "subtotal": subtotal
            })
        cursor.execute(
            "INSERT INTO ventas (total) VALUES (%s)",
            (total_venta,)
        )
        venta_id = cursor.lastrowid
        for item in detalle_calculado:
            cursor.execute("""
                INSERT INTO detalle_ventas (
                    venta_id,
                    producto_id,
                    cantidad,
                    precio_unitario,
                    subtotal
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                venta_id,
                item["producto_id"],
                item["cantidad"],
                item["precio_unitario"],
                item["subtotal"]
            ))
            cursor.execute("""
                UPDATE productos
                SET stock = stock - %s
                WHERE id_producto = %s
            """, (
                item["cantidad"],
                item["producto_id"]
            ))
        conn.commit()
        return jsonify({
            "mensaje": "Venta registrada correctamente",
            "id_venta": venta_id,
            "total": total_venta,
            "detalle": detalle_calculado
        }), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@ventas_bp.route("/mas-vendidos", methods=["GET"])
def mas_vendidos():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.nombre, p.tipo, p.precio,
                   SUM(dv.cantidad) as total_vendido,
                   SUM(dv.subtotal) as total_ingresos
            FROM detalle_ventas dv
            JOIN productos p ON dv.producto_id = p.id_producto
            GROUP BY p.id_producto
            ORDER BY total_vendido DESC
            LIMIT 10
        """)
        productos = cursor.fetchall()
        return jsonify({"mas_vendidos": productos}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()