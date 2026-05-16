from flask import Blueprint, jsonify, request
from db.db_conn import get_connection

reseñas_bp = Blueprint("reseñas", __name__)