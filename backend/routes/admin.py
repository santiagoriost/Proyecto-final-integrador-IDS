from flask import Blueprint, jsonify, request
from db.db_conn import get_connection

administradores_bp = Blueprint("administradores", __name__)