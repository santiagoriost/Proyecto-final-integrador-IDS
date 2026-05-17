from flask import Blueprint, jsonify, request
from db.db_conn import get_connection
from .utils import validar_atributos_producto
from db.queries.productos_queries import verificar_producto
from db.queries.local_queries import obtener_nombre_local
productos_bp = Blueprint("productos", __name__)

@productos_bp.route("/", methods=["GET"])
def listar_productos():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        limit = int(request.args.get("_limit", 10))
        offset = int(request.args.get("_offset", 0))

        query = "SELECT * FROM productos LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        lista_productos = cursor.fetchall()
        if not lista_productos:
            return jsonify({"error": "productos no encontrados"}), 404
        
        query_cant_productos = "SELECT COUNT(*) as total FROM productos"
        cursor.execute(query_cant_productos)
        cant_productos = cursor.fetchone()["total"]

        productos = []
        for producto in lista_productos:
            productos.append({
                "id": producto["id_producto"],
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "stock": producto["stock"],
                "tipo": producto["tipo"],
                "local": producto["local_producto"]
            })
        
        base_url = request.base_url
        def build_url(new_offset):
            params = f"_limit={limit}&_offset={new_offset}"
            #despues podemos aplicar la opcion de buscar por atributo pero bueno ahora no tengo ganas
            return f"{base_url}?{params}"
        links = {
            "_first": {"href": build_url(0)},
            "_last": {"href": build_url(max(cant_productos - (cant_productos % 10), cant_productos - limit))}
        }
        if offset > 0:
            links["_prev"] = {"href": build_url(max(offset - limit, 0))}
        if offset + limit < cant_productos:
            links["_next"] = {"href": build_url(offset + limit)}

        return jsonify({
            "productos": productos,
            "_links": links
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@productos_bp.route("/", methods=["POST"])
def agregar_producto():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)
        datos = request.get_json()

        error_validacion = validar_atributos_producto(datos)
        if error_validacion:
            return error_validacion
        
        local_nombre = obtener_nombre_local(datos["local_producto"], cursor)
        if not local_nombre:
            return jsonify({"error": "el local indicado no existe"}), 404
        
        valores = (datos["nombre"], datos["precio"], datos["stock"], datos["tipo"], datos["local_producto"])
        query = """
        INSERT INTO productos(nombre, precio, stock, tipo, local_producto)
        VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, valores)
        conn.commit()
        return jsonify({
            "id": cursor.lastrowid,
            "nombre": datos["nombre"],
            "precio": datos["precio"],
            "stock": datos["stock"],
            "tipo": datos["tipo"],
            "local": local_nombre
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn: 
            conn.close()

@productos_bp.route("/<int:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)
        query_verificacion = "SELECT * FROM productos WHERE id_producto = %s"
        cursor.execute(query_verificacion, (id_producto,))
        producto = cursor.fetchone()
        if not producto:
            return jsonify({"error": "producto no encontrado"}), 404
        query_eliminar = "DELETE FROM productos WHERE id_producto = %s"
        cursor.execute(query_eliminar, (id_producto,))
        conn.commit()
        return jsonify({
            "mensaje": "producto eliminado correctamente",
            "producto_eliminado": producto
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@productos_bp.route("/<int:id_producto>", methods=["GET"])
def listar_producto(id_producto):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)

        producto = verificar_producto(id_producto, cursor)
        if not producto:
            return jsonify({"error": "producto no encontrado"}), 404
        
        local_nombre = obtener_nombre_local(producto["local_producto"], cursor)

        return jsonify({
            "id": producto["id_producto"],
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "stock": producto["stock"],
            "tipo": producto["tipo"],
            "local": local_nombre
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@productos_bp.route("/<int:id_producto>", methods=["PUT"])
def actualizar_producto(id_producto):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)
        datos = request.get_json()

        error_validacion = validar_atributos_producto(datos)
        if error_validacion:
            return error_validacion
        
        producto = verificar_producto(id_producto, cursor)
        if not producto:
            return jsonify({"error": "producto no encontrado"}), 404

        local_nombre = obtener_nombre_local(datos["local_producto"], cursor)
        if not local_nombre:
            return jsonify({"error": "el local indicado no existe"}), 404
            
        valores = (datos["nombre"], datos["precio"], datos["stock"], datos["tipo"], datos["local_producto"], id_producto)
        query = """
            UPDATE productos
            SET nombre = %s, precio = %s, stock = %s, tipo = %s, local_producto = %s
            WHERE id_producto = %s
        """
        cursor.execute(query, valores)
        conn.commit()
        producto_actualizado = {
            "id": id_producto,
            "nombre": datos["nombre"],
            "precio": datos["precio"],
            "stock": datos["stock"],
            "tipo": datos["tipo"],
            "local": local_nombre
        }
        return jsonify({
            "mensaje": "producto actualizado correctamente",
            "producto_actualizado": producto_actualizado
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()