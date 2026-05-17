from flask import jsonify
def validar_atributos_producto(datos):
    if not datos:
        return jsonify({"error": "no se especificaron los atributos"}), 400
    atributos_necesarios = ("nombre", "precio", "stock", "tipo", "local_producto")
    for atributo in atributos_necesarios:
        if atributo not in datos:
            return jsonify({"error": "atributo %s no especificado" %atributo}), 400
        if str(datos[atributo]).strip() == "":
            return jsonify({"error": "el atributo %s tiene un valor vacio" %atributo}), 400
        elif atributo == "precio" and not isinstance(datos["precio"], (int, float)):
            return jsonify({"error": "atributo %s no es un dato de tipo INT / FLOAT" %atributo}), 400
        elif atributo in ("stock", "local_producto") and not str(datos[atributo]).isdigit():
            return jsonify({"error": "atributo %s tiene que ser de tipo INT" %atributo}), 400
        elif atributo in ("nombre", "tipo") and not isinstance(datos[atributo], str):
            return jsonify({"error": "el atributo %s tiene que ser tipo str" %atributo}), 400