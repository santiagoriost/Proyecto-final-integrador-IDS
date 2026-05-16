from flask import Blueprint, jsonify, request
from db.db_conn import get_connection

usuarios_bp = Blueprint("usuarios", __name__)