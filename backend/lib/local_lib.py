from flask import jsonify

def obtener_nombre_local(id_local, cursor):
    query_local = "SELECT nombre FROM locales WHERE id_local = %s"
    cursor.execute(query_local, (id_local,))
    local_nombre = cursor.fetchone()
    if local_nombre:
        return local_nombre.get("nombre")
