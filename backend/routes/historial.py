from flask import Blueprint, jsonify, request
from db.db_conn import get_connection
historial_bp = Blueprint("historial", __name__)

@historial_bp.route("/historial/", methods=["GET"])
def get_historial():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM historial_acciones ORDER BY fecha DESC LIMIT 100"
        )
        historial = cursor.fetchall()
        cursor.close()
        conn.close()
        # convertir datetime a string para que jsonify lo acepte
        for item in historial:
            if item.get("fecha"):
                item["fecha"] = item["fecha"].strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({"historial": historial}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@historial_bp.route("/historial/", methods=["POST"])
def registrar_accion():
    datos = request.get_json()
    accion  = datos.get("accion", "")
    tipo    = datos.get("tipo", "")
    detalle = datos.get("detalle", "")
    if not accion or not tipo:
        return jsonify({"error": "accion y tipo son requeridos"}), 400
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO historial_acciones (accion, tipo, detalle) VALUES (%s, %s, %s)",
            (accion, tipo, detalle)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensaje": "Acción registrada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500