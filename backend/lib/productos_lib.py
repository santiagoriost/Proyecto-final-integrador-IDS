from flask import jsonify
def obtener_registros(cursor, limit, offset):
    query = "SELECT * FROM productos LIMIT %s OFFSET %s"
    cursor.execute(query, (limit, offset))
    return cursor.fetchall()

def cantidad_productos(cursor):
    cursor.execute("SELECT COUNT(*) as total FROM productos")
    return cursor.fetchone()["total"]
    
def obtener_producto(id_producto, cursor):
    query_verificacion = "SELECT * FROM productos WHERE id_producto = %s"
    cursor.execute(query_verificacion, (id_producto,))
    producto = cursor.fetchone()
    return producto

def validar_tipo_dato(datos, atributo):
    valor = datos[atributo]
    if str(valor).strip() == "":
        return jsonify({"error": "el atributo %s tiene un valor vacio" %atributo}), 400
    elif atributo == "precio":
        try:
            datos["precio"] = float(valor)
            if datos["precio"] < 0:
                return jsonify({"error": "el precio no puede ser negativo"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "atributo %s no es un dato de tipo INT / FLOAT" %atributo}), 400
    elif atributo in ("stock", "local_producto"):
        try:
            datos[atributo] = int(valor)
            if datos[atributo] < 0:
                return jsonify({"error": "el atributo %s no puede ser negativo" %atributo}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "el atributo %s tiene que ser de tipo INT" %atributo}), 400
    elif atributo in ("nombre", "tipo"):
        if not isinstance(valor, str):
            return jsonify({"error": "el atributo %s tiene que ser tipo str" %atributo}), 400

def validar_atributos_necesarios(datos):
    if not datos:
        return jsonify({"error": "no se especificaron los atributos"}), 400
    atributos_necesarios = ("nombre", "precio", "stock", "tipo", "local_producto")
    for atributo in atributos_necesarios:
        if atributo not in datos:
            return jsonify({"error": "atributo %s no especificado" %atributo}), 400
        error_tipo_dato = validar_tipo_dato(datos, atributo)
        if error_tipo_dato:
            return error_tipo_dato

def generar_url(base_url, limit, new_offset):
    params = f"_limit={limit}&_offset={new_offset}"
    return f"{base_url}?{params}"

def generar_links(base_url, limit, cant_productos, offset):
    links = {
        "_first": {"href": generar_url(base_url, limit, 0)},
        "_last": {"href": generar_url(base_url, limit, max(cant_productos - (cant_productos % 10), cant_productos - limit))}
    }
    if offset > 0:
        links["_prev"] = {"href": generar_url(base_url, limit, max(offset - limit, 0))}
    if offset + limit < cant_productos:
        links["_next"] = {"href": generar_url(base_url, limit, offset + limit)}
    return links
