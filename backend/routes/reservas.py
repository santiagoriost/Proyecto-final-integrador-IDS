from flask import Blueprint, jsonify, request
from db.db_conn import get_connection

reservas_bp = Blueprint("reservas", __name__)