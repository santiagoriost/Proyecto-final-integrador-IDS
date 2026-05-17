from flask import jsonify

def verificar_producto(id_producto, cursor):
    query_verificacion = "SELECT * FROM productos WHERE id_producto = %s"
    cursor.execute(query_verificacion, (id_producto,))
    producto = cursor.fetchone()
    return producto
