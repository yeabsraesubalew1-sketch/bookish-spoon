from flask import Blueprint, request, jsonify, render_template, abort, session

from db.models import cur, conn, is_session_set

products_bp = Blueprint("products", __name__)
