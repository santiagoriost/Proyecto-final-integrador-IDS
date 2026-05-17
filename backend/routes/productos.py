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