from flask import Blueprint, request, jsonify, render_template, session

from db.models import cur, is_session_set

search_bp = Blueprint("search", __name__)
