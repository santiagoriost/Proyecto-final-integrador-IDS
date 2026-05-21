from flask import Blueprint, jsonify, request
from db.db_conn import get_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
from lib.productos_lib import obtener_producto, validar_atributos_necesarios, validar_tipo_dato, obtener_registros, cantidad_productos, generar_links
from lib.local_lib import obtener_nombre_local
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

        lista_productos = obtener_registros(cursor, limit, offset)
        if not lista_productos:
            return jsonify({"error": "productos no encontrados"}), 404
        cant_productos = cantidad_productos(cursor)
        
        productos = []
        for producto in lista_productos:
            nombre_local = obtener_nombre_local(producto["local_producto"], cursor)
            productos.append({
                "id": producto["id_producto"],
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "stock": producto["stock"],
                "tipo": producto["tipo"],
                "local": nombre_local
            })
        base_url = request.base_url
        links = generar_links(base_url, limit, cant_productos, offset)
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
#@jwt_required()
def agregar_producto():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)
        #usuario_logueado = get_jwt_identity()
        #if usuario_logueado["rol"] != "admin":
        #    return jsonify({"error": "acceso denegado"}), 403
        
        datos = request.get_json()
        error_validacion = validar_atributos_necesarios(datos)
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
#@jwt_required()
def eliminar_producto(id_producto):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)
        #usuario_logueado = get_jwt_identity()
        #if usuario_logueado["rol"] != "admin":
        #    return jsonify({"error": "acceso denegado"}), 403

        producto = obtener_producto(id_producto, cursor)
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

        producto = obtener_producto(id_producto, cursor)
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
#@jwt_required()
def actualizar_producto(id_producto):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)
        #usuario_logueado = get_jwt_identity()
        #if usuario_logueado["rol"] != "admin":
        #    return jsonify({"error": "acceso denegado"}), 403

        datos = request.get_json()
        error_validacion = validar_atributos_necesarios(datos)
        if error_validacion:
            return error_validacion
        
        producto = obtener_producto(id_producto, cursor)
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

@productos_bp.route("/<int:id_producto>", methods=["PATCH"])
#@jwt_required()
def modificar_producto(id_producto):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)

        #usuario_logueado = get_jwt_identity()
        #if usuario_logueado["rol"] != "admin":
        #    return jsonify({"error": "acceso denegado"}), 403
        
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "atributos no especificados"}), 400
        if not obtener_producto(id_producto, cursor):
            return jsonify({"error": "producto no encontrado"}), 404
        
        atributos_validos = ["nombre", "precio", "stock", "tipo", "local"]
        query = "UPDATE productos SET "
        sentencias = []
        valores = []
        for atributo in datos:
            if atributo not in atributos_validos:
                return jsonify({"error": "atributo no valido"}), 400
            error_tipo_dato = validar_tipo_dato(datos, atributo)
            if error_tipo_dato:
                return error_tipo_dato
            sentencias.append(f"{atributo} = %s")
            valores.append(datos[atributo])
        query += ", ".join(sentencias)
        query += f" WHERE id_producto = %s"
        valores.append(id_producto)
        cursor.execute(query, valores)
        conn.commit()

        producto_modificado = obtener_producto(id_producto, cursor)
        return jsonify({
            "mensaje": "producto modificado correctamente",
            "producto_modificacdo": producto_modificado
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()