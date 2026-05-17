from flask import Blueprint, jsonify, request
from db.db_conn import get_connection

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
        if not datos:
            return jsonify({"error": "no se recibieron atributos"}), 400
        atributos_necesarios = ("nombre", "precio", "stock", "tipo", "local_producto")
        for atributo in atributos_necesarios:
            if atributo not in datos:
                return jsonify({"error": "atributo %s no encontrado" %atributo}), 400
            if str(datos[atributo]).strip() == "":
                return jsonify({"error": "el atributo %s tiene un valor vacio" %atributo}), 400
            elif atributo == "precio" and not isinstance(datos["precio"], (int, float)):
                return jsonify({"error": "atributo %s no es un dato de tipo INT / FLOAT" %atributo}), 400
            elif atributo in ("stock", "local_producto") and not str(datos[atributo]).isdigit():
                return jsonify({"error": "atributo %s tiene que ser de tipo INT" %atributo}), 400
            elif atributo in ("nombre", "tipo") and not isinstance(datos[atributo], str):
                return jsonify({"error": "el atributo %s tiene que ser tipo str" %atributo}), 400
        
        query_local = "SELECT nombre FROM locales WHERE id_local=%s"
        cursor.execute(query_local, (datos["local_producto"],))
        local_nombre = cursor.fetchone()["nombre"]
        if not local_nombre:
            return jsonify({"error": "local no encontrado (id = %s)" %datos["local_producto"]}), 404
        
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
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn: 
            conn.close()